"""
OCR accuracy report (Sprint B #1204).

Runs every image listed in sample-images/expected.json through
OCR -> parse -> typo fix -> swaps and prints a Markdown table.

    cd backend
    python evaluate_ocr.py
"""

import json
import time
from pathlib import Path

from ingredient_parser import fix_ocr_typos, parse_ingredients
from ocr import read_label
from replacements import find_replacements

SAMPLES = Path(__file__).resolve().parent.parent / "sample-images"


def main():
    expected = json.loads((SAMPLES / "expected.json").read_text())
    total_found = total_expected = 0

    print("| Image | Difficulty | Expected found | Swaps | Clean-up used | Rotated | Confidence | Time |")
    print("|---|---|---|---|---|---|---|---|")
    for name, info in expected.items():
        start = time.time()
        ocr = read_label((SAMPLES / name).read_bytes())
        ingredients, corrections = fix_ocr_typos(parse_ingredients(ocr["text"]))
        swaps = find_replacements(ingredients)
        seconds = time.time() - start

        found = [item for item in info["expected"] if item in ingredients]
        total_found += len(found)
        total_expected += len(info["expected"])
        print(f"| {name} | {info['difficulty']} | {len(found)}/{len(info['expected'])} | {len(swaps)} "
              f"| {ocr['method']} | {ocr['rotated']}° | {ocr['confidence']}% | {seconds:.1f}s |")

        missing = [item for item in info["expected"] if item not in ingredients]
        if missing or corrections:
            notes = []
            if corrections:
                notes.append("typo fixes: " + ", ".join(f"{c['from']} → {c['to']}" for c in corrections))
            if missing:
                notes.append("missed: " + ", ".join(missing))
            print(f"|  | ↳ {'; '.join(notes)} | | | | | | |")

    print(f"\n**Total: {total_found}/{total_expected} expected ingredients found "
          f"({100 * total_found / total_expected:.0f}%)**")


if __name__ == "__main__":
    main()
