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

---

# Sprint B (due Friday, November 13)

**Goal:** users can get reliable healthier ingredient suggestions from a wider range of food-label images.

Full evidence, numbers and screenshots: [docs/SPRINT_B_EVIDENCE.md](docs/SPRINT_B_EVIDENCE.md)

## Cards and files
| Card | Owner | Files |
|---|---|---|
| #1204 Improve OCR Accuracy | Mohamed | `backend/ocr.py`, `backend/ingredient_parser.py`, `backend/evaluate_ocr.py`, `sample-images/*` + `generate_samples.py` + `expected.json`, `backend/tests/test_ocr_samples.py`, `backend/tests/test_parser.py` |
| #1205 Expand Replacement Database | Henry | `backend/data/replacements.json`, `backend/replacements.py`, `backend/tests/test_replacements.py` |
| #1206 Improve Frontend UI & Results Display | Anthony | `frontend/src/components/SwapResults.jsx`, `frontend/src/App.jsx`, `frontend/src/App.css` |
| #1207 Image Upload & Validation Improvements | Alejandro | `backend/validation.py`, `backend/main.py`, `frontend/src/validation.js`, `frontend/src/components/ImageUpload.jsx`, `backend/tests/test_api.py` (builds on PR #2 large-image handling) |
| #1208 Integration, Testing & Evidence | Ali | `backend/main.py`, `backend/tests/*`, `backend/requirements-dev.txt`, `docs/SPRINT_B_EVIDENCE.md`, `docs/sprint-b-evidence/*.png`, `README.md`, this file |

## Acceptance criteria status

**#1204 Improve OCR Accuracy**
- [x] Improved preprocessing for harder images: rotation detection, even-lighting and sharpening clean-ups, best result chosen automatically
- [x] Ingredients extracted from at least 2 different test images: 6 different labels, 5 of them hard
- [x] Clean-label behaviour preserved: `cookie-label.png` gives the same 13 ingredients and 8 swaps (tested)
- [x] Test results documented (Sprint A 50% → Sprint B 88%, in the evidence doc)

**#1205 Expand Ingredient Replacement Database**
- [x] 36 new swaps (28 → 63), so at least 15–20 new
- [x] Each has replacement, reason and category (tested)
- [x] Existing logic still works: whole-word and longest-match tests pass
- [x] No obvious false positives: `never_swap` list, plus 14 negative tests

**#1206 Improve Frontend UI & Results Display**
- [x] Two-column upload/results layout
- [x] Clear loading (spinner + status card) and error states
- [x] Original (grey, struck through) vs replacement (green) in "Instead of → Try" columns
- [x] Detected ingredients (swap ones highlighted) and raw OCR text readable
- [x] Works at 1280/1366 px laptop widths and stacks below 860 px (no horizontal scroll, tested)

**#1207 Image Upload & Validation Improvements**
- [x] Supported types validated in browser and server (extension, MIME type, real file format)
- [x] Unsupported files show a clear error (.txt, .pdf, HEIC, GIF renamed to .png)
- [x] Empty, damaged, too-small and blank images fail cleanly
- [x] PNG, JPG, WEBP, BMP and TIFF uploads all succeed (tested)
- [x] Existing valid uploads still work

**#1208 Sprint B Integration, Testing & Evidence**
- [x] All improvements work together (browser end-to-end run, 22 checks)
- [x] Full flow works on 6 different label images
- [x] Evidence for each card in `docs/SPRINT_B_EVIDENCE.md`
- [x] No app errors in the browser console or backend log during the demo flow

## Sprint B demo script (about 5 minutes)
1. Start backend and frontend (see README). Show http://127.0.0.1:8000: `"swaps_available": 63`.
2. **Clean label still works:** upload `cookie-label.png` → 8 swaps. Point out the summary, "Instead of → Try" and highlighted chips. (#1206)
3. **Harder photos:** upload `cereal-rotated.jpg` ("turned 270°") and `soda-shadow-noisy.jpg` ("even lighting" clean-up). (#1204)
4. **Low-quality photo:** upload `crackers-blurry-lowres.jpg` → low-confidence warning and "Fixed OCR misreads: smortening → shortening". (#1204)
5. **New swaps:** in the soda/cereal results, point to new entries (caramel color, phosphoric acid, BHT, canola oil) with category badges. (#1205)
6. **Validation:** drag in a `.txt` or `.pdf` → instant clear error; use Remove; upload a blank image → "No text was found". (#1207)
7. **Evidence:** run `python -m pytest` (80 passed) and `python evaluate_ocr.py` (88%). (#1208)

## Out of scope (Sprint B)
Authentication, database, user accounts, deployment, non-English labels, HEIC conversion.
