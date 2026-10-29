"""
Ingredient Swap App - FastAPI backend.

Flow for POST /analyze:
    uploaded image -> OCR text -> parsed ingredients -> healthier swaps -> JSON
"""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ingredient_parser import parse_ingredients
from ocr import OCRError, extract_text
from replacements import find_replacements

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

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
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PNG, JPG, WEBP, BMP or TIFF image.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="The image is too large (max 10 MB).")

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
