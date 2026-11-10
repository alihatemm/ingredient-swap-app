"""
Ingredient parsing.

Turns raw OCR text such as

    INGREDIENTS: Enriched flour (wheat flour, niacin), sugar,
    palm oil, salt. CONTAINS: WHEAT.

into a clean list:

    ["enriched flour", "wheat flour", "niacin", "sugar", "palm oil", "salt"]

Sprint B (#1204) adds fix_ocr_typos(), which repairs small OCR misreads such as
"smortening" -> "shortening" using a list of words we know.
"""

import difflib
import re

from replacements import REPLACEMENTS

# Words that mark the end of the ingredient list on most labels.
STOP_WORDS = ["contains:", "contains ", "allergen", "may contain", "manufactured", "distributed by",
              "nutrition facts", "phenylketonurics", "keep refrigerated", "best by"]

# Filler phrases that show up inside ingredient lists but are not ingredients.
# These are removed BEFORE looking for stop words, so "contains 2% or less of"
# in the middle of the list does not cut the list short.
FILLER_PHRASES = [
    "contains 2% or less of",
    "contains less than 2% of",
    "contains one or more of the following",
    "2% or less of",
    "less than 2% of",
    "to preserve freshness",
    "to preserve flavor",
    "for freshness",
    "for color",
    "as a preservative",
    "and/or",
]

# Common label words that are NOT in the swap list. Typo fixing must never
# "correct" these into something else, and may correct misreads towards them.
KNOWN_WORDS = """
water wheat flour whole grain oats rolled corn rice brown white sugar syrup honey salt sea
milk cheese cultures enzymes cream butter eggs egg whites yolks soy lecithin soybean canola
sunflower safflower olive coconut palm kernel oil oils vegetable natural artificial flavor
flavors flavoring spices spice garlic onion powder paprika extract turmeric annatto vanilla
cocoa chocolate liquor baking soda leavening yeast vinegar citric acid ascorbic malic lactic
tomato paste puree concentrate juice apple lemon orange raisins peanuts almonds cashews
niacin reduced iron thiamine mononitrate riboflavin folic vitamin mineral calcium potassium
sodium phosphate chloride carbonate bicarbonate sorbate benzoate nitrite citrate caseinate
monosodium glutamate dextrose fructose glucose maltodextrin molasses caramel color colour
starch modified cornstarch gum xanthan guar cellulose pectin gelatin carrageenan
preservative preserve freshness tocopherols protein isolate whey dried nonfat skim
shortening hydrogenated partially cottonseed enriched bleached unbleached degerminated
mozzarella cheddar parmesan pepperoni pork beef chicken bacon carbonated caffeine aspartame
sucralose phosphoric tripotassium mustard pepper black cinnamon nutmeg ginger
sucrose lactose maltose galactose sorbitol xylitol erythritol maltitol stevia inulin
batter""".split()


def build_vocabulary():
    words = set(KNOWN_WORDS)
    for key in REPLACEMENTS:
        words.update(key.split())
    return sorted(w for w in words if len(w) >= 3)


VOCABULARY = build_vocabulary()
VOCABULARY_SET = set(VOCABULARY)

# Only long words are fixed (short words have too many look-alikes), and only
# when they are very similar to a known word (0.85 = 85% the same letters).
MIN_TYPO_LENGTH = 6
TYPO_SIMILARITY = 0.85


def isolate_ingredient_section(text):
    """Keep only the part of the text after 'ingredients' and before e.g. 'contains:'."""
    lower = text.lower()

    start = lower.find("ingredients")
    if start != -1:
        # Skip the word "ingredients" and a following colon if present.
        start += len("ingredients")
        lower = lower[start:].lstrip(" :;.-")
    # If no "ingredients" header was found, use the whole text.

    # Remove filler first so "contains 2% or less of" is not mistaken for "contains:".
    for phrase in FILLER_PHRASES:
        lower = lower.replace(phrase, ",")

    for stop in STOP_WORDS:
        index = lower.find(stop)
        if index > 0:
            lower = lower[:index]

    return lower


def clean_ingredient(item):
    """Remove stray characters and extra spaces from one ingredient."""
    item = re.sub(r"[^a-z0-9%&/\- ]", " ", item)  # keep letters, digits and a few symbols
    item = re.sub(r"\s+", " ", item).strip(" -/&")
    if item.startswith("and "):
        item = item[4:]
    return item.strip()


def parse_ingredients(text):
    """Convert raw OCR text into a list of ingredient names."""
    if not text or not text.strip():
        return []

    section = isolate_ingredient_section(text)

    # Join words broken across lines with a hyphen ("hydro-\ngenated"),
    # then turn remaining line breaks into spaces.
    section = re.sub(r"-\s*\n\s*", "", section)
    section = section.replace("\n", " ")

    # Parentheses hold sub-ingredients, so they separate items.
    # Square/curly brackets and "|" on labels are almost always OCR noise
    # ("caramel] color"), so they are simply removed.
    section = re.sub(r"[()]", ",", section)
    section = re.sub(r"[\[\]{}|]", "", section)

    raw_items = re.split(r"[,;.:]", section)

    ingredients = []
    for item in raw_items:
        name = clean_ingredient(item)
        # Ignore empty bits and OCR noise (1-2 characters).
        if len(name) > 2 and name not in ingredients:
            ingredients.append(name)

    return ingredients


def fix_word(word):
    """Return the known word this looks like, or the word unchanged."""
    if len(word) < MIN_TYPO_LENGTH or word in VOCABULARY_SET or not word.isalpha():
        return word
    matches = difflib.get_close_matches(word, VOCABULARY, n=1, cutoff=TYPO_SIMILARITY)
    return matches[0] if matches else word


def fix_ocr_typos(ingredients):
    """
    Repair small OCR misreads, word by word.

    Returns (fixed_ingredients, corrections) where corrections is a list of
    {"from": ..., "to": ...} so the user can see exactly what was changed.
    """
    fixed_ingredients = []
    corrections = []
    for ingredient in ingredients:
        fixed = " ".join(fix_word(word) for word in ingredient.split())
        if fixed != ingredient:
            corrections.append({"from": ingredient, "to": fixed})
        if fixed not in fixed_ingredients:
            fixed_ingredients.append(fixed)
    return fixed_ingredients, corrections
