"""
Ingredient Swap App - FastAPI backend.

Flow for POST /analyze:
    uploaded image -> validate -> OCR text -> parsed ingredients
                   -> fix OCR typos -> healthier swaps -> JSON
"""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ingredient_parser import fix_ocr_typos, parse_ingredients
from ocr import OCRError, read_label
from replacements import REPLACEMENTS, find_replacements
from validation import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UploadError, validate_upload

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
    return {
        "status": "ok",
        "message": "Ingredient Swap API is running",
        "swaps_available": len(REPLACEMENTS),
        "accepted_files": sorted(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
    }


# A plain "def" (not "async def"): FastAPI runs it in a worker thread, so a slow
# OCR request does not freeze the server for other requests.
@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    """Take an ingredient-list image and return ingredients plus healthier swaps."""

    # 1. Validate the upload (see validation.py).
    image_bytes = file.file.read()
    try:
        validate_upload(file.filename, file.content_type, image_bytes)
    except UploadError as error:
        raise HTTPException(status_code=error.status, detail=str(error))

    # 2. OCR: image -> text (see ocr.py).
    try:
        ocr = read_label(image_bytes)
    except OCRError as error:
        raise HTTPException(status_code=422, detail=str(error))

    text = ocr["text"]
    if not text:
        raise HTTPException(
            status_code=422,
            detail="No text was found in the image. Try a clearer, well-lit photo of the ingredient list.",
        )

    # 3. Parse text -> ingredient list, then repair small OCR misreads.
    ingredients, corrections = fix_ocr_typos(parse_ingredients(text))

    # 4. Replacement logic.
    suggestions = find_replacements(ingredients)

    # 5. Structured response for the frontend. The first four fields are the
    #    same as Sprint A; "ocr" and "corrections" are new in Sprint B.
    return {
        "filename": file.filename,
        "extracted_text": text,
        "ingredients": ingredients,
        "suggestions": suggestions,
        "ocr": {
            "method": ocr["method"],
            "confidence": ocr["confidence"],
            "rotated": ocr["rotated"],
        },
        "corrections": corrections,
    }
