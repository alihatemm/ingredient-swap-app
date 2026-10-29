# ingredient-swap-app
Sprint A project that extracts ingredients from food-label images and suggests healthier replacements.

## What it does

1. You upload a photo of a food label's ingredient list.
2. The backend reads the text from the image with OCR (Tesseract).
3. The text is split into a clean list of ingredients.
4. Each ingredient is checked against a list of common swaps.
5. The page shows each match as **original ingredient → healthier replacement**, with a short reason.

## Stack

| Part | Tech |
|---|---|
| Frontend | React (Vite) |
| Backend | FastAPI (Python) |
| OCR | Tesseract via `pytesseract` + Pillow |
| Replacement data | Python dictionary (`backend/replacements.py`) |

## Project structure

```
ingredient-swap-app/
├── backend/
│   ├── main.py               # FastAPI app: GET / (health) and POST /analyze
│   ├── ocr.py                # Ingredient Text Extraction (image -> text)
│   ├── ingredient_parser.py  # text -> list of ingredients
│   ├── replacements.py       # Ingredient Replacement Logic (swap dictionary)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                     # page state: file, loading, error, result
│       ├── App.css
│       ├── api.js                      # sends the image to /analyze
│       └── components/
│           ├── ImageUpload.jsx         # Image Upload card
│           └── SwapResults.jsx         # Display Swap Suggestions card
├── sample-images/
│   └── cookie-label.png      # supported test image for the demo
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

- Health check: http://localhost:8000 → `{"status": "ok", ...}`
- Interactive API docs: http://localhost:8000/docs (you can test `/analyze` there)

Quick test from a second terminal (repo root):

```bash
curl -F "file=@sample-images/cookie-label.png" http://localhost:8000/analyze
```

## Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, choose `sample-images/cookie-label.png`, and click **Find healthier swaps**.

The frontend calls `http://localhost:8000` by default. To use another backend URL, create `frontend/.env` with `VITE_API_URL=http://your-host:port`.

## How the flow works

```
React (ImageUpload)                     FastAPI (/analyze)
  choose image  ──── POST multipart ──▶  1. validate file type / size / empty
  preview + name                         2. ocr.extract_text()       image -> text
  loading state                          3. parse_ingredients()      text -> ["sugar", "palm oil", ...]
                                         4. find_replacements()      ingredient -> healthier swap
React (SwapResults)  ◀──── JSON ───────  5. return result
  original → replacement
  ingredients found + raw OCR text
```

Example response from `POST /analyze`:

```json
{
  "filename": "cookie-label.png",
  "extracted_text": "INGREDIENTS:\nEnriched flour (wheat flour, niacin, reduced iron),\nsugar, palm oil, ...",
  "ingredients": ["enriched flour", "wheat flour", "niacin", "reduced iron", "sugar", "palm oil", "..."],
  "suggestions": [
    {
      "original": "palm oil",
      "matched": "palm oil",
      "replacement": "olive oil",
      "reason": "Less saturated fat and more heart-healthy fats."
    }
  ]
}
```

### Errors the backend handles

| Situation | Status | Message |
|---|---|---|
| Not an image (e.g. .pdf, .txt) | 400 | Unsupported file type |
| Empty file | 400 | The uploaded file is empty |
| Over 10 MB | 400 | The image is too large |
| Corrupt / unreadable image | 422 | The file could not be read as an image |
| Image with no readable text | 422 | No text was found in the image |
| Tesseract missing | 422 | Tesseract OCR is not installed on the server |

The frontend shows these messages in a red box, plus a clear message if the backend is not running.

## Adding more swaps

Open `backend/replacements.py` and add an entry to `REPLACEMENTS`:

```python
"white sugar": {
    "replacement": "coconut sugar",
    "reason": "Less refined.",
},
```

Matching is by whole words, and the longest match wins (so "high fructose corn syrup" beats "corn syrup").

## Known limitations

- OCR works best on clear, flat, well-lit photos of printed text. Curved packages, glare, or tiny fonts reduce accuracy.
- Only English labels are supported.
- iPhone HEIC photos are not supported — export as JPG/PNG first.
- Swaps come from a fixed list of ~30 common ingredients; anything not in the list gets no suggestion.
- Suggestions are general cooking/nutrition ideas, not medical or dietary advice.
