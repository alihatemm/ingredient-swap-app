"""
Ingredient Replacement Logic.

The swap data lives in data/replacements.json so it is easy to edit without
touching Python code (Sprint B #1205):

    "swaps":      ingredient -> healthier replacement, short reason, category
    "never_swap": phrases that must never get a suggestion, e.g. "cocoa butter"
                  (contains "butter") or "whole wheat flour" (contains "wheat flour")
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "replacements.json"

with open(DATA_FILE, encoding="utf-8") as f:
    _data = json.load(f)

REPLACEMENTS = _data["swaps"]
NEVER_SWAP = _data["never_swap"]

# Longest keys first so the most specific match wins
# ("high fructose corn syrup" before "corn syrup").
_KEYS_LONGEST_FIRST = sorted(REPLACEMENTS.keys(), key=len, reverse=True)


def contains_phrase(text, phrase):
    """True if phrase appears in text as whole words ("salt" is in "sea salt", not in "unsalted")."""
    return f" {phrase} " in f" {text} "


def find_match(ingredient):
    """Return the replacement key that matches this ingredient, or None."""
    name = ingredient.lower()

    if any(contains_phrase(name, phrase) for phrase in NEVER_SWAP):
        return None  # already healthy, or a different ingredient (cocoa butter is not butter)

    for key in _KEYS_LONGEST_FIRST:
        if contains_phrase(name, key):
            return key
    return None


def find_replacements(ingredients):
    """
    Build one suggestion for each ingredient that has a healthier swap.

    Matching is done on whole words, preferring the longest key, so
    "high fructose corn syrup" matches that entry instead of plain "corn syrup",
    and "sugar" will match "cane sugar" but "salt" won't match "unsalted".
    """
    suggestions = []
    for ingredient in ingredients:
        key = find_match(ingredient)
        if key is None:
            continue
        suggestions.append(
            {
                "original": ingredient,
                "matched": key,
                "replacement": REPLACEMENTS[key]["replacement"],
                "reason": REPLACEMENTS[key]["reason"],
                "category": REPLACEMENTS[key]["category"],
            }
        )
    return suggestions
