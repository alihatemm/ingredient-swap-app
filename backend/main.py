"""
Ingredient Swap App - FastAPI backend.

Flow for POST /analyze:
    uploaded image -> OCR text -> parsed ingredients -> healthier swaps -> JSON
"""

import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from ingredient_parser import parse_ingredients
from ocr import OCRError, extract_text
from replacements import find_replacements

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"}
# Real formats as Pillow names them. Some phone cameras save JPEGs that Pillow reads as MPO.
ALLOWED_FORMATS = {"PNG", "JPEG", "MPO", "WEBP", "BMP", "TIFF"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
UNSUPPORTED_TYPE_MESSAGE = "Unsupported file type. Please upload a PNG, JPG, WEBP, BMP or TIFF image."

app = FastAPI(title="Ingredient Swap App")

# Allow the React dev server (Vite) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    """Health check: confirms the backend is running."""
    return {"status": "ok", "message": "Ingredient Swap API is running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    """Take an ingredient-list image and return ingredients plus healthier swaps."""

    # 1. Validate the upload.
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=UNSUPPORTED_TYPE_MESSAGE)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="The image is too large (max 10 MB).")

    # Check the real format from the file's contents; the content type is only a label.
    # Files Pillow can't open (corrupt, or too many pixels) get their clear error from OCR below.
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            real_format = image.format
    except (Image.DecompressionBombError, OSError):  # UnidentifiedImageError is an OSError
        real_format = None
    if real_format is not None and real_format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail=UNSUPPORTED_TYPE_MESSAGE)

    # 2. OCR: image -> text.
    try:
        text = extract_text(image_bytes)
    except OCRError as error:
        raise HTTPException(status_code=422, detail=str(error))

    if not text:
        raise HTTPException(
            status_code=422,
            detail="No text was found in the image. Try a clearer, well-lit photo of the ingredient list.",
        )

    # 3. Parse text -> ingredient list.
    ingredients = parse_ingredients(text)

    # 4. Replacement logic.
    suggestions = find_replacements(ingredients)

    # 5. Structured response for the frontend.
    return {
        "filename": file.filename,
        "extracted_text": text,
        "ingredients": ingredients,
        "suggestions": suggestions,
    }
