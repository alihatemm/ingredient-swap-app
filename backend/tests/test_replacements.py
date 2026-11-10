"""#1205 Expand Ingredient Replacement Database."""

import json

import pytest

from replacements import DATA_FILE, NEVER_SWAP, REPLACEMENTS, find_replacements

# The 28 swaps that existed at the end of Sprint A.
SPRINT_A_KEYS = {
    "sugar", "high fructose corn syrup", "corn syrup", "white flour", "enriched flour",
    "bleached flour", "wheat flour", "palm oil", "hydrogenated oil", "partially hydrogenated oil",
    "vegetable oil", "shortening", "butter", "margarine", "salt", "sodium", "white rice",
    "milk chocolate", "cream", "sour cream", "mayonnaise", "artificial flavors", "artificial flavor",
    "monosodium glutamate", "msg", "aspartame", "sucralose", "dextrose",
}


def swap_for(ingredient):
    suggestions = find_replacements([ingredient])
    return suggestions[0]["matched"] if suggestions else None


def test_at_least_20_new_swaps():
    new_keys = set(REPLACEMENTS) - SPRINT_A_KEYS
    assert len(new_keys) >= 20, sorted(new_keys)


def test_every_swap_has_replacement_reason_and_category():
    for key, swap in REPLACEMENTS.items():
        assert key == key.lower().strip(), key
        assert swap["replacement"].strip(), key
        assert swap["reason"].strip(), key
        assert swap["category"].strip(), key


def test_data_file_is_valid_json():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    assert "swaps" in data and "never_swap" in data


@pytest.mark.parametrize("ingredient, expected_key", [
    # Sprint A behaviour still works
    ("sugar", "sugar"),
    ("cane sugar", "sugar"),
    ("high fructose corn syrup", "high fructose corn syrup"),  # longest match wins
    ("corn syrup", "corn syrup"),
    ("enriched flour", "enriched flour"),
    ("palm oil", "palm oil"),
    ("sea salt", "salt"),
    ("artificial flavors", "artificial flavors"),
    # New in Sprint B
    ("partially hydrogenated soybean oil", "partially hydrogenated"),
    ("soybean oil", "soybean oil"),
    ("brown rice syrup", "brown rice syrup"),
    ("caramel color", "caramel color"),
    ("sodium benzoate", "sodium benzoate"),
    ("sodium nitrite", "sodium nitrite"),
    ("bht", "bht"),
    ("yellow 5", "yellow 5"),
    ("red 40", "red 40"),
    ("maltodextrin", "maltodextrin"),
    ("phosphoric acid", "phosphoric acid"),
    ("chocolate chips", "chocolate chips"),
    ("cheddar cheese", "cheddar cheese"),
    ("palm kernel oil", "palm kernel oil"),
])
def test_matches(ingredient, expected_key):
    assert swap_for(ingredient) == expected_key


@pytest.mark.parametrize("ingredient", [
    # whole-word matching (Sprint A)
    "unsalted almonds",          # not "salt"
    "sugarcane fiber",           # not "sugar"
    "buttermilk",                # not "butter"
    # false positives that Sprint A got wrong, fixed by never_swap / specific keys
    "whole wheat flour",         # used to suggest "whole wheat flour" -> "whole wheat flour"
    "cocoa butter",              # not butter
    "peanut butter",
    "cream of tartar",           # a leavening agent, not cream
    "sodium ascorbate",          # vitamin C; Sprint A suggested "herbs and spices"
    "sodium bicarbonate",        # baking soda
    "olive oil",                 # already the healthy option
    # ordinary ingredients with no swap
    "water", "niacin", "rolled oats", "tomato paste",
])
def test_no_false_positives(ingredient):
    assert swap_for(ingredient) is None


def test_suggestion_fields():
    [suggestion] = find_replacements(["palm oil"])
    assert suggestion == {
        "original": "palm oil",
        "matched": "palm oil",
        "replacement": "olive oil",
        "reason": REPLACEMENTS["palm oil"]["reason"],
        "category": "fat & oil",
    }


def test_never_swap_entries_are_not_swap_keys():
    assert not set(NEVER_SWAP) & set(REPLACEMENTS)
