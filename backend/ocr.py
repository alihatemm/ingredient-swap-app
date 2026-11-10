"""
Ingredient Text Extraction (OCR).

Uses Tesseract through the pytesseract library. Tesseract itself must be
installed on the computer (see README.md).

Sprint B (#1204): real photos are often rotated, dark, blurry or unevenly lit,
so instead of one fixed clean-up we now:

  1. prepare the image   - fix phone rotation, grayscale, enlarge small photos
  2. find which way is up - if the text reads badly, try turning it 90/180/270
  3. try a few clean-ups - "standard", "even lighting", "sharp black & white"
  4. keep the best one   - the version with the most words Tesseract is sure about

Tesseract is told to treat the image as one block of text (--psm 6), which
matches an ingredient panel and works much better on small, blurry photos.
"""

import io
import os
import re

import pytesseract
from PIL import Image, ImageChops, ImageFilter, ImageOps, UnidentifiedImageError

# On Windows, Tesseract is often not on the PATH. Setting the TESSERACT_CMD
# environment variable to the full path of tesseract.exe fixes that.
if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]

TARGET_SIZE = 1600  # small photos are enlarged until their longest side is this many pixels
TESSERACT_CONFIG = "--psm 6"  # "assume a single uniform block of text"
SURE_CONFIDENCE = 70  # a word read with at least this confidence counts as a "good" word
UPRIGHT_GOOD_WORDS = 8  # if the image already gives this many good words, it is upright


class OCRError(Exception):
    """Raised when an image cannot be read or OCR fails."""


# ---------------------------------------------------------------------------
# Step 1 and 2: prepare and straighten
# ---------------------------------------------------------------------------

def prepare(image):
    """Fix phone rotation, convert to grayscale and enlarge small images."""
    image = ImageOps.exif_transpose(image)  # phones store rotation in EXIF data
    image = image.convert("L")  # grayscale

    longest = max(image.size)
    if longest < TARGET_SIZE:
        scale = TARGET_SIZE / longest
        image = image.resize((int(image.width * scale), int(image.height * scale)), Image.LANCZOS)
    return image


def find_upright(image):
    """
    Turn the image so the text is upright. Returns (image, degrees_turned).

    Sideways text comes out as nonsense with very few "good" words, so if the
    image reads badly we simply try the other three directions and keep the
    one that reads best.
    """
    best_image, best_angle = image, 0
    best_count = good_word_count(read_words(standard(image)))
    if best_count >= UPRIGHT_GOOD_WORDS:
        return image, 0  # reads fine already (the usual case)

    for angle in (90, 180, 270):
        turned = image.rotate(angle, expand=True, fillcolor=255)
        count = good_word_count(read_words(standard(turned)))
        if count > best_count:
            best_image, best_angle, best_count = turned, angle, count
    return best_image, best_angle


# ---------------------------------------------------------------------------
# Step 3: different clean-ups for different problems
# ---------------------------------------------------------------------------

def standard(image):
    """Stretch the contrast. Enough for clean, well-lit labels."""
    return ImageOps.autocontrast(image, cutoff=1)


def even_lighting(image):
    """
    Remove shadows and dark corners.

    A heavy blur keeps only the background lighting (the text disappears).
    Subtracting the image from that background leaves just the text, with the
    shadow gone. Then we flip it back to dark text on white.
    """
    background = image.filter(ImageFilter.GaussianBlur(radius=max(image.size) // 40))
    text_only = ImageChops.subtract(background, image)  # text bright, background ~0
    return ImageOps.autocontrast(ImageOps.invert(text_only), cutoff=1)


def sharp_black_and_white(image):
    """Sharpen blurry text, then turn every pixel pure black or white."""
    image = ImageOps.autocontrast(image, cutoff=2)
    image = image.filter(ImageFilter.MedianFilter(3))  # remove camera noise speckles
    image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    threshold = otsu_threshold(image)
    return image.point(lambda p: 255 if p > threshold else 0)


def otsu_threshold(image):
    """
    Pick the gray level that best separates dark text from light background
    (Otsu's method: the split where the two groups are most different).
    """
    histogram = image.histogram()
    total = sum(histogram)
    sum_all = sum(i * count for i, count in enumerate(histogram))
    sum_dark, count_dark, best_threshold, best_score = 0, 0, 128, 0
    for level in range(256):
        count_dark += histogram[level]
        if count_dark == 0 or count_dark == total:
            continue
        sum_dark += level * histogram[level]
        mean_dark = sum_dark / count_dark
        mean_light = (sum_all - sum_dark) / (total - count_dark)
        score = count_dark * (total - count_dark) * (mean_dark - mean_light) ** 2
        if score > best_score:
            best_score, best_threshold = score, level
    return best_threshold


CLEANUPS = [
    ("standard", standard),
    ("even lighting", even_lighting),
    ("sharp black & white", sharp_black_and_white),
]


# ---------------------------------------------------------------------------
# Step 4: read each version and keep the best result
# ---------------------------------------------------------------------------

def read_words(image):
    """
    Run Tesseract and return a list of (word, confidence, line_id).
    confidence is 0-100: how sure Tesseract is about that word.
    """
    data = pytesseract.image_to_data(image, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)
    words = []
    for i, word in enumerate(data["text"]):
        confidence = float(data["conf"][i])
        if word.strip() and confidence >= 0:
            line_id = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            words.append((word.strip(), confidence, line_id))
    return words


def good_word_count(words):
    """How many real-looking words (3+ letters) Tesseract is sure about."""
    return sum(1 for word, confidence, _ in words
               if confidence >= SURE_CONFIDENCE and re.search(r"[A-Za-z]{3,}", word))


def words_to_text(words):
    """Put the words back together, one line of the label per line of text."""
    lines = {}
    for word, _, line_id in words:
        lines.setdefault(line_id, []).append(word)
    return "\n".join(" ".join(line) for line in lines.values())


def open_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except Image.DecompressionBombError as error:
        raise OCRError(
            "The image resolution is too large to process. Please upload a lower-resolution photo."
        ) from error
    except (UnidentifiedImageError, OSError) as error:
        raise OCRError("The file could not be read as an image.") from error
    return image


def read_label(image_bytes):
    """
    Read the text on a label photo.

    Returns a dict:
        text        - the text found
        method      - which clean-up gave the best result
        confidence  - Tesseract's average word confidence for that result (0-100)
        rotated     - degrees the image was turned to make it upright
    """
    image = open_image(image_bytes)

    try:
        image = prepare(image)
        image, rotated = find_upright(image)

        best_words, best_method, best_count = [], CLEANUPS[0][0], -1
        for name, cleanup in CLEANUPS:
            words = read_words(cleanup(image))
            count = good_word_count(words)
            if count > best_count:  # on a tie the earlier (simpler) clean-up wins
                best_words, best_method, best_count = words, name, count
    except pytesseract.TesseractNotFoundError as error:
        raise OCRError(
            "Tesseract OCR is not installed on the server. See README.md for setup."
        ) from error

    confidences = [confidence for _, confidence, _ in best_words]
    return {
        "text": words_to_text(best_words).strip(),
        "method": best_method,
        "confidence": round(sum(confidences) / len(confidences)) if confidences else 0,
        "rotated": rotated,
    }


def extract_text(image_bytes):
    """Return only the text found in an image (kept for Sprint A code and tests)."""
    return read_label(image_bytes)["text"]
