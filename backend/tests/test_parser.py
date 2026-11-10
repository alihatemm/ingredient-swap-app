"""Ingredient parsing and OCR typo fixing (#1204)."""

from ingredient_parser import fix_ocr_typos, parse_ingredients


def test_sprint_a_example():
    text = """INGREDIENTS: Enriched flour (wheat flour, niacin, reduced iron),
sugar, palm oil, high fructose corn syrup, salt, unsalted butter, artificial fla-
vors, soy lecithin. CONTAINS: WHEAT, SOY."""
    assert parse_ingredients(text) == [
        "enriched flour", "wheat flour", "niacin", "reduced iron", "sugar", "palm oil",
        "high fructose corn syrup", "salt", "unsalted butter", "artificial flavors", "soy lecithin",
    ]


def test_empty_text():
    assert parse_ingredients("") == []
    assert parse_ingredients("   \n ") == []


def test_contains_2_percent_does_not_cut_the_list():
    # Sprint A bug: "contains " was treated as the allergen line and cut the list here.
    text = "Ingredients: water, sugar, contains 2% or less of: salt, yellow 5. Contains: milk."
    assert parse_ingredients(text) == ["water", "sugar", "salt", "yellow 5"]


def test_ocr_bracket_noise_does_not_split_ingredients():
    text = "INGREDIENTS: sea salt, caramel] color, cocoa butter|."
    assert parse_ingredients(text) == ["sea salt", "caramel color", "cocoa butter"]


def test_filler_phrases_removed():
    text = "Ingredients: canola oil, BHT (to preserve freshness), citric acid (for color)."
    assert parse_ingredients(text) == ["canola oil", "bht", "citric acid"]


def test_warning_line_is_not_an_ingredient():
    text = "Ingredients: carbonated water, aspartame. PHENYLKETONURICS: CONTAINS PHENYLALANINE."
    assert parse_ingredients(text) == ["carbonated water", "aspartame"]


def test_fix_ocr_typos():
    fixed, corrections = fix_ocr_typos(["smortening", "gextrose", "peprika extract", "sugar"])
    assert fixed == ["shortening", "dextrose", "paprika extract", "sugar"]
    assert {"from": "smortening", "to": "shortening"} in corrections
    assert len(corrections) == 3


def test_fix_ocr_typos_leaves_real_words_alone():
    # Similar to known words but real, different ingredients: must NOT change.
    words = ["batter", "sucrose", "fructose", "lactose", "cultures", "salt", "sat"]
    fixed, corrections = fix_ocr_typos(words)
    assert fixed == words
    assert corrections == []
