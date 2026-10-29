"""
Ingredient parsing.

Turns raw OCR text such as

    INGREDIENTS: Enriched flour (wheat flour, niacin), sugar,
    palm oil, salt. CONTAINS: WHEAT.

into a clean list:

    ["enriched flour", "wheat flour", "niacin", "sugar", "palm oil", "salt"]
"""

import re

# Words that mark the end of the ingredient list on most labels.
STOP_WORDS = ["contains:", "contains ", "allergen", "may contain", "manufactured", "distributed by", "nutrition facts"]

# Filler phrases that show up inside ingredient lists but are not ingredients.
FILLER_PHRASES = [
    "contains 2% or less of",
    "contains less than 2% of",
    "2% or less of",
    "less than 2% of",
    "and/or",
]


def isolate_ingredient_section(text):
    """Keep only the part of the text after 'ingredients' and before e.g. 'contains:'."""
    lower = text.lower()

    start = lower.find("ingredients")
    if start != -1:
        # Skip the word "ingredients" and a following colon if present.
        start += len("ingredients")
        lower = lower[start:].lstrip(" :;.-")
    # If no "ingredients" header was found, use the whole text.

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

    for phrase in FILLER_PHRASES:
        section = section.replace(phrase, ",")

    # Treat brackets as separators so sub-ingredients become their own items.
    section = re.sub(r"[()\[\]{}]", ",", section)

    raw_items = re.split(r"[,;.]", section)

    ingredients = []
    for item in raw_items:
        name = clean_ingredient(item)
        # Ignore empty bits and OCR noise (1-2 characters).
        if len(name) > 2 and name not in ingredients:
            ingredients.append(name)

    return ingredients
