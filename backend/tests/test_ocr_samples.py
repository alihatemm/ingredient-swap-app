"""
#1204 Improve OCR Accuracy.

Runs the full OCR -> parse -> typo-fix pipeline on every image in
sample-images/expected.json and checks how many expected ingredients are found.
Needs Tesseract installed. For a readable report run:  python evaluate_ocr.py
"""

import json

import pytest

from conftest import SAMPLES
from ingredient_parser import fix_ocr_typos, parse_ingredients
from ocr import read_label
from replacements import find_replacements

EXPECTED = json.loads((SAMPLES / "expected.json").read_text())

# Minimum share of expected ingredients that must be found per image.
# The tiny blurry cracker photo is the known hard case (see README limitations).
MIN_RECALL = {"crackers-blurry-lowres.jpg": 0.4}


def run(name):
    ocr = read_label((SAMPLES / name).read_bytes())
    ingredients, _ = fix_ocr_typos(parse_ingredients(ocr["text"]))
    return ocr, ingredients


@pytest.mark.parametrize("name", list(EXPECTED))
def test_sample_image(name):
    ocr, ingredients = run(name)
    expected = EXPECTED[name]["expected"]
    found = [e for e in expected if e in ingredients]
    assert len(found) / len(expected) >= MIN_RECALL.get(name, 1.0), (ocr["method"], ingredients)
    assert find_replacements(ingredients), "every sample should get at least one swap"


def test_clean_label_unchanged_from_sprint_a():
    ocr, ingredients = run("cookie-label.png")
    assert ocr["method"] == "standard" and ocr["rotated"] == 0
    assert ingredients == [
        "enriched flour", "wheat flour", "niacin", "reduced iron", "sugar", "palm oil",
        "high fructose corn syrup", "cocoa", "salt", "butter", "soy lecithin",
        "artificial flavors", "baking soda",
    ]


def test_sideways_photo_is_turned_upright():
    ocr, _ = run("cereal-rotated.jpg")
    assert ocr["rotated"] in (90, 270)


def test_shadowed_photo_uses_even_lighting():
    ocr, _ = run("soda-shadow-noisy.jpg")
    assert ocr["method"] == "even lighting"
