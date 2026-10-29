# Implementation Plan

## Stack
- Frontend: React
- Backend: FastAPI / Python
- OCR: ingredient text extraction
- Replacement data: Python dictionary or JSON

## Flow
1. User uploads an ingredient-list image.
2. Frontend sends the image to the backend.
3. Backend extracts the ingredient text.
4. Extracted text is parsed into a list of ingredients.
5. Replacement logic finds healthier alternatives.
6. Frontend displays ingredient → replacement suggestions.

## Where each card lives in the code
| Card | Files |
|---|---|
| Image Upload | `frontend/src/components/ImageUpload.jsx` |
| Ingredient Text Extraction | `backend/ocr.py`, `backend/ingredient_parser.py` |
| Ingredient Replacement Logic | `backend/replacements.py` |
| Display Swap Suggestions | `frontend/src/components/SwapResults.jsx` |
| End-to-End Integration & Demo | `backend/main.py` (`/analyze`), `frontend/src/api.js`, `frontend/src/App.jsx`, `sample-images/cookie-label.png` |

## Acceptance criteria status
- [x] User can upload an ingredient-list image.
- [x] Ingredients from the image are extracted successfully.
- [x] At least one matching healthier replacement suggestion is displayed.
- [x] With `sample-images/cookie-label.png`, the app shows replacement suggestions with no manual data entry between steps (8 swaps in testing).

## Demo script
1. Start backend (`uvicorn main:app --reload --port 8000`) and frontend (`npm run dev`).
2. Open http://localhost:5173 and choose `sample-images/cookie-label.png`.
3. Click **Find healthier swaps** → show the swaps, the ingredient list and the raw OCR text.
4. Optional: upload a non-image or blank image to show error handling.

## Out of scope (Sprint A)
Authentication, database, user accounts, deployment.

## Ownership
- Alejandro: Image Upload
- Mohamed: Ingredient Text Extraction
- Henry: Ingredient Replacement Logic
- Anthony: Display Swap Suggestions
- Ali: End-to-End Integration & Demo
