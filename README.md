# ingredient-swap-app
Capstone project that extracts ingredients from food-label images and suggests healthier replacements.

**Sprint A** built the working flow. **Sprint B** (due Nov 13) makes it reliable on harder photos, adds more swaps, polishes the UI and tightens upload validation. See [What changed in Sprint B](#what-changed-in-sprint-b) and the full evidence in [docs/SPRINT_B_EVIDENCE.md](docs/SPRINT_B_EVIDENCE.md).

## What it does

1. You upload (or drag in) a photo of a food label's ingredient list.
2. The upload is checked in the browser and again on the server.
3. The backend reads the text with OCR (Tesseract). It straightens sideways photos and tries a few image clean-ups, keeping whichever reads best.
4. The text is split into a clean list of ingredients, and small OCR misreads are repaired.
5. Each ingredient is checked against 63 common swaps.
6. The page shows each match as **Instead of → Try**, with a short reason and category.

## Stack

| Part | Tech |
|---|---|
| Frontend | React (Vite) |
| Backend | FastAPI (Python) |
| OCR | Tesseract via `pytesseract` + Pillow |
| Replacement data | JSON file (`backend/data/replacements.json`) |
| Tests | pytest + FastAPI TestClient |

## Project structure

```
ingredient-swap-app/
├── backend/
│   ├── main.py               # FastAPI app: GET / (health) and POST /analyze
│   ├── validation.py         # #1207 upload checks with friendly messages
│   ├── ocr.py                # #1204 image -> text (rotation + 3 clean-ups, best one wins)
│   ├── ingredient_parser.py  # text -> list of ingredients, OCR typo fixes
│   ├── replacements.py       # #1205 matching logic
│   ├── data/replacements.json  # #1205 the swap database (edit this to add swaps)
│   ├── evaluate_ocr.py       # #1204 prints an OCR accuracy table for the sample images
│   ├── tests/                # pytest tests (80 tests)
│   ├── requirements.txt
│   └── requirements-dev.txt  # pytest + httpx, only needed to run tests
├── frontend/
│   └── src/
│       ├── App.jsx                     # page layout and state
│       ├── App.css
│       ├── api.js                      # sends the image to /analyze
│       ├── validation.js               # #1207 checks in the browser before upload
│       └── components/
│           ├── ImageUpload.jsx         # pick / drag & drop, preview, file info
│           └── SwapResults.jsx         # #1206 summary, swaps, ingredients, OCR text
├── sample-images/            # 6 test labels (clean + 5 hard ones) and expected.json
│   └── generate_samples.py   # recreates the hard test images
├── docs/
│   ├── SPRINT_B_EVIDENCE.md  # card-by-card evidence and test results
│   └── sprint-b-evidence/    # screenshots
├── README.md
└── IMPLEMENTATION_PLAN.md
```

## Requirements

- Python 3.10+
- Node.js 20.19+ (needed by Vite 7)
- **Tesseract OCR** installed on your computer (system program, not a pip package)

### Installing Tesseract

| OS | Command |
|---|---|
| macOS | `brew install tesseract` |
| Ubuntu / Debian | `sudo apt install tesseract-ocr` |
| Windows | Install from https://github.com/UB-Mannheim/tesseract/wiki and tick "Add to PATH" (or note the install folder, usually `C:\Program Files\Tesseract-OCR`) |

Check it worked: `tesseract --version`

**Windows only:** if the app says Tesseract is not installed even though it is, set the path before starting the backend:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

- Health check: http://127.0.0.1:8000 → `{"status": "ok", "swaps_available": 63, ...}`
- Interactive API docs: http://127.0.0.1:8000/docs (you can test `/analyze` there)

Quick test from a second terminal (repo root):

```bash
curl -F "file=@sample-images/cereal-rotated.jpg" http://127.0.0.1:8000/analyze
```

## Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, choose any image from `sample-images/`, and click **Find healthier swaps**.

The frontend calls `http://127.0.0.1:8000` by default. To use another backend URL, create `frontend/.env` with `VITE_API_URL=http://your-host:port`.

## Run the tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest            # 80 tests: swaps, parser, validation, OCR on every sample, API
python evaluate_ocr.py      # OCR accuracy table for the sample images
```

## How the flow works

```
React (ImageUpload + validation.js)          FastAPI (/analyze)
  pick / drop image, checked in browser ─ POST ─▶ 1. validate_upload()   type, size, real format, pixels
  preview, name, size, Remove                     2. read_label()        rotate if needed, 3 clean-ups,
  spinner while loading                                                   keep the one that reads best
                                                  3. parse_ingredients() text -> ["sugar", "palm oil", ...]
                                                     fix_ocr_typos()     "smortening" -> "shortening"
                                                  4. find_replacements() ingredient -> healthier swap
React (SwapResults)  ◀──────── JSON ──────────── 5. return result
  summary · Instead of → Try · ingredients · raw OCR text
```

Example response from `POST /analyze`. The first four fields are unchanged from Sprint A; `category`, `ocr` and `corrections` are new:

```json
{
  "filename": "crackers-blurry-lowres.jpg",
  "extracted_text": "INGREDIENTS:\nEnnched wheat flour, soybean of. cheddar cheese ...",
  "ingredients": ["ennched wheat flour", "cheddar cheese", "shortening", "sugar", "..."],
  "suggestions": [
    {
      "original": "shortening",
      "matched": "shortening",
      "replacement": "olive oil or unsweetened applesauce",
      "reason": "Cuts saturated and trans fats.",
      "category": "fat & oil"
    }
  ],
  "ocr": {"method": "standard", "confidence": 59, "rotated": 0},
  "corrections": [{"from": "smortening", "to": "shortening"}]
}
```

### Upload errors

Checked in the browser first (`frontend/src/validation.js`), then again on the server (`backend/validation.py`):

| Situation | Status | Message (shortened) |
|---|---|---|
| Wrong file kind (.pdf, .txt, .gif…) | 400 | '.pdf' files are not supported. Please upload a PNG, JPG, WEBP, BMP or TIFF image. |
| iPhone HEIC photo | 400 | iPhone HEIC photos are not supported yet. Please export the photo as JPG… |
| Image renamed to a wrong extension (GIF saved as .png) | 400 | Unsupported file type… |
| Empty file | 400 | The uploaded file is empty. Please choose the photo again. |
| Over 10 MB | 400 | The image is too large (12.3 MB). The limit is 10 MB. |
| Damaged / not really an image | 422 | The file is damaged or is not really an image… |
| Smaller than 50 px | 422 | The image is too small to read (30x20 pixels)… |
| Resolution too large (over ~179 megapixels) | 422 | The image resolution is too large to process… |
| Image with no readable text | 422 | No text was found in the image… |
| Tesseract missing | 422 | Tesseract OCR is not installed on the server… |

Photos larger than 4000 px are shrunk in the browser before upload, and the frontend shows a clear message if the backend is not running.

## What changed in Sprint B

| Card | Owner | Change |
|---|---|---|
| #1204 Improve OCR Accuracy | Mohamed | Sideways photos are turned upright; three clean-ups ("standard", "even lighting" for shadows, "sharp black & white" for blur) are tried and the best is kept; small photos are enlarged; Tesseract reads the label as one text block; OCR misreads like "smortening" are fixed; parser bugs fixed. **Accuracy on the 6 test labels: 50% → 88%** of expected ingredients, swaps found 19 → 37. |
| #1205 Expand Replacement Database | Henry | Swaps moved to `data/replacements.json` and grown from 28 to **63** (36 new, each with replacement, reason and category). New `never_swap` list fixes Sprint A false positives such as *whole wheat flour → whole wheat flour* and *cocoa butter → olive oil*. |
| #1206 Improve Frontend UI | Anthony | Two-column layout on laptops (stacks on narrow screens), summary counts, "Instead of → Try" table with category badges, highlighted ingredients that have swaps, OCR details, low-confidence warning, spinner and empty state. |
| #1207 Upload & Validation | Alejandro | Matching checks in the browser and on the server: extension, type, HEIC, empty, size, real format, too-small images. Drag & drop, file size/dimensions shown, Remove button. Builds on the large-image handling already merged in PR #2. |
| #1208 Integration & Evidence | Ali | 80 automated backend tests, browser end-to-end run with screenshots, OCR accuracy script, docs and evidence file. |

## Adding more swaps

Open `backend/data/replacements.json` and add an entry under `"swaps"`:

```json
"white sugar": {"replacement": "coconut sugar", "reason": "Less refined.", "category": "sweetener"}
```

- Matching is by whole words, and the longest match wins, so "high fructose corn syrup" beats "corn syrup".
- If a swap matches something it shouldn't (like "butter" inside "cocoa butter"), add that phrase to `"never_swap"`.
- Run `python -m pytest tests/test_replacements.py` afterwards.

## Known limitations

- OCR works best on clear, flat, well-lit photos of printed text. Very small or very blurry photos are still only partly read: the 470-pixel-wide blurry test image gets 4 of 9 ingredients. The app shows a warning when OCR confidence is below 70%.
- The hard test images are synthetic. They are made to copy real problems (rotation, darkness, blur, shadow, white-on-dark), but each photo was not taken of a real package. Test with a few real phone photos before the demo.
- Curved packages, glare and strong perspective (photo taken at an angle) are not corrected.
- Only English labels are supported.
- iPhone HEIC photos are not supported; export as JPG/PNG first. Most browsers can't preview TIFF files, but they still upload and work.
- OCR typo fixing only changes long words that are very similar to a known word, so some misreads stay as they are. Every change is shown to the user.
- Swaps come from a fixed list of 63 ingredients; anything not in the list gets no suggestion.
- Analysis takes about 1–2 seconds per photo because several clean-ups are tried.
- Suggestions are general cooking/nutrition ideas, not medical or dietary advice.
