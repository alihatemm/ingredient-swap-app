"""
Generates the Sprint B test images in this folder.

Each image is a different food label made harder to read in a different way
(rotated, dark, blurry, uneven lighting, white-on-dark...). They are synthetic
so anyone on the team can recreate them, but each "hard" effect copies a real
problem we see in phone photos of packaging.

Run from the repo root:
    python sample-images/generate_samples.py

It also writes expected.json, which lists the ingredients each image should
produce. backend/tests/test_ocr_samples.py uses it to measure OCR accuracy.
"""

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).parent
FONT_DIRS = ["/usr/share/fonts", "/Library/Fonts", "/System/Library/Fonts", "C:/Windows/Fonts"]


def find_font(names):
    for folder in FONT_DIRS:
        for name in names:
            matches = list(Path(folder).rglob(name)) if Path(folder).exists() else []
            if matches:
                return str(matches[0])
    raise SystemExit(f"None of these fonts were found: {names}")


SANS = find_font(["DejaVuSans.ttf", "Arial.ttf", "arial.ttf"])
SANS_BOLD = find_font(["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf"])
CONDENSED = find_font(["DejaVuSansCondensed.ttf", "LiberationSans-Regular.ttf", "Arial.ttf", "arial.ttf"])


def draw_label(lines, footer, font_path=SANS, size=34, width=1200, fg="black", bg="white"):
    """Draw a simple label: INGREDIENTS: header, wrapped lines, CONTAINS footer."""
    font = ImageFont.truetype(font_path, size)
    bold = ImageFont.truetype(SANS_BOLD, size + 4)
    line_height = int(size * 1.6)
    height = 60 + 70 + line_height * len(lines) + 120
    img = Image.new("RGB", (width, height), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, width - 20, height - 20], outline=fg, width=4)
    y = 50
    d.text((50, y), "INGREDIENTS:", font=bold, fill=fg)
    y += 70
    for line in lines:
        d.text((50, y), line, font=font, fill=fg)
        y += line_height
    d.text((50, y + 20), footer, font=bold, fill=fg)
    return img


def on_table(label, margin=120, color=(190, 175, 150)):
    """Put the label on a coloured background, like a photo of a package on a table."""
    canvas = Image.new("RGB", (label.width + 2 * margin, label.height + 2 * margin), color)
    canvas.paste(label, (margin, margin))
    return canvas


def add_noise(img, amount=25, seed=1):
    rnd = random.Random(seed)
    noise = Image.effect_noise(img.size, amount).convert("RGB")
    return Image.blend(img, noise, 0.18 + rnd.random() * 0.02)


def shadow_gradient(img, strength=0.65):
    """Darken one side of the image, like a shadow from a hand or lamp."""
    w, h = img.size
    mask = Image.linear_gradient("L").rotate(90).resize((w, h))  # left bright -> right dark
    dark = ImageEnhance.Brightness(img).enhance(1 - strength)
    return Image.composite(img, dark, mask)


SAMPLES = [
    {
        # Sprint A image (clean). Kept as is so we know clean labels still work.
        "file": "cookie-label.png",
        "difficulty": "clean (Sprint A baseline)",
        "existing": True,
        "expected": ["enriched flour", "sugar", "palm oil", "high fructose corn syrup", "salt",
                     "butter", "artificial flavors"],
    },
    {
        "file": "cereal-rotated.jpg",
        "difficulty": "photo taken sideways (rotated 90 degrees)",
        "lines": ["Whole grain oats, sugar, corn syrup, honey,",
                  "brown sugar syrup, salt, canola oil, tripotassium",
                  "phosphate, natural flavor, BHT (to preserve freshness)."],
        "footer": "CONTAINS: OATS.",
        "make": lambda img: on_table(img).rotate(90, expand=True).convert("RGB"),
        "expected": ["sugar", "corn syrup", "brown sugar syrup", "salt", "canola oil", "bht"],
    },
    {
        "file": "granola-bar-dark.jpg",
        "difficulty": "dark, low-contrast photo with a slight tilt",
        "lines": ["Rolled oats, brown rice syrup, chocolate chips",
                  "(sugar, chocolate liquor, cocoa butter), sunflower",
                  "oil, molasses, white rice flour, sea salt, caramel color."],
        "footer": "MAY CONTAIN PEANUTS.",
        "make": lambda img: ImageEnhance.Contrast(
            ImageEnhance.Brightness(on_table(img).rotate(-4, expand=True, fillcolor=(190, 175, 150))).enhance(0.38)
        ).enhance(0.55),
        "expected": ["brown rice syrup", "chocolate chips", "sugar", "sunflower oil", "white rice flour",
                     "sea salt", "caramel color"],
    },
    {
        "file": "crackers-blurry-lowres.jpg",
        "difficulty": "small, blurry, low-quality JPEG",
        "lines": ["Enriched wheat flour, soybean oil, cheddar cheese",
                  "(milk, salt, cultures), shortening, sugar, dextrose,",
                  "monosodium glutamate, yellow 5, paprika extract."],
        "footer": "CONTAINS: WHEAT, MILK.",
        "make": lambda img: on_table(img).resize((470, 245)).filter(ImageFilter.GaussianBlur(1.1)),
        "jpeg_quality": 30,
        "expected": ["enriched wheat flour", "soybean oil", "cheddar cheese", "salt", "shortening", "sugar",
                     "dextrose", "monosodium glutamate", "yellow 5"],
    },
    {
        "file": "soda-shadow-noisy.jpg",
        "difficulty": "uneven lighting (shadow) and camera noise",
        "lines": ["Carbonated water, high fructose corn syrup,",
                  "caramel color, phosphoric acid, natural flavors,",
                  "sodium benzoate, caffeine, aspartame."],
        "footer": "PHENYLKETONURICS: CONTAINS PHENYLALANINE.",
        "make": lambda img: add_noise(shadow_gradient(on_table(img), 0.7)),
        "expected": ["high fructose corn syrup", "caramel color", "phosphoric acid", "sodium benzoate",
                     "aspartame"],
    },
    {
        "file": "pizza-white-on-dark.png",
        "difficulty": "white text on a dark background, condensed font",
        "lines": ["Crust (bleached flour, water, partially hydrogenated",
                  "soybean oil, sugar, yeast), mozzarella cheese, tomato",
                  "paste, pepperoni (pork, salt, sodium nitrite), cream."],
        "footer": "CONTAINS: WHEAT, MILK.",
        "font": CONDENSED,
        "fg": "white",
        "bg": (35, 25, 25),
        "make": lambda img: img,
        "expected": ["bleached flour", "partially hydrogenated soybean oil", "sugar", "mozzarella cheese",
                     "sodium nitrite", "cream"],
    },
]


def main():
    expected = {}
    for sample in SAMPLES:
        expected[sample["file"]] = {"difficulty": sample["difficulty"], "expected": sample["expected"]}
        if sample.get("existing"):
            continue
        label = draw_label(sample["lines"], sample["footer"], font_path=sample.get("font", SANS),
                           fg=sample.get("fg", "black"), bg=sample.get("bg", "white"))
        img = sample["make"](label).convert("RGB")
        path = HERE / sample["file"]
        if path.suffix == ".jpg":
            img.save(path, quality=sample.get("jpeg_quality", 70))
        else:
            img.save(path)
        print(f"wrote {path.name:28} {img.size[0]}x{img.size[1]}  ({sample['difficulty']})")

    (HERE / "expected.json").write_text(json.dumps(expected, indent=2) + "\n")
    print("wrote expected.json")


if __name__ == "__main__":
    main()
