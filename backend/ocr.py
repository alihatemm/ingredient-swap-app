"""
Ingredient Text Extraction (OCR).

Uses Tesseract through the pytesseract library. Tesseract itself must be
installed on the computer (see README.md).
"""

import io
import os

import pytesseract
from PIL import Image, ImageOps, UnidentifiedImageError

# On Windows, Tesseract is often not on the PATH. Setting the TESSERACT_CMD
# environment variable to the full path of tesseract.exe fixes that.
if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]


class OCRError(Exception):
    """Raised when an image cannot be read or OCR fails."""


def preprocess(image):
    """Simple clean-up that helps Tesseract read printed labels."""
    image = ImageOps.exif_transpose(image)  # fix rotated phone photos
    image = image.convert("L")  # grayscale

    # Small images OCR badly, so scale them up.
    if image.width < 1000:
        scale = 1000 / image.width
        image = image.resize((int(image.width * scale), int(image.height * scale)))

    image = ImageOps.autocontrast(image)
    return image


def extract_text(image_bytes):
    """Return the text found in an image (given as raw bytes)."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
    except (UnidentifiedImageError, OSError) as error:
        raise OCRError("The file could not be read as an image.") from error

    try:
        text = pytesseract.image_to_string(preprocess(image))
    except pytesseract.TesseractNotFoundError as error:
        raise OCRError(
            "Tesseract OCR is not installed on the server. See README.md for setup."
        ) from error

    return text.strip()
