# Backend (FastAPI)

| File | Card | What it does |
|---|---|---|
| `main.py` | Integration | `GET /` health check, `POST /analyze` runs the full pipeline, CORS for `localhost:5173` |
| `validation.py` | #1207 Upload & Validation | Extension, content type, HEIC, empty, size, real format and pixel-size checks with friendly messages |
| `ocr.py` | #1204 OCR Accuracy | Enlarges small photos, turns sideways photos upright, tries 3 clean-ups ("standard", "even lighting", "sharp black & white") and keeps the one that reads best |
| `ingredient_parser.py` | #1204 / Text Extraction | Keeps the text between "Ingredients:" and "Contains:", splits on commas/brackets, cleans each item, fixes small OCR misreads |
| `replacements.py` | #1205 Replacement Logic | Whole-word, longest-match lookup with a "never swap" list |
| `data/replacements.json` | #1205 Replacement Database | The 63 swaps (replacement, reason, category). Edit this file to add more |
| `evaluate_ocr.py` | #1204 | Prints an accuracy table for every image in `sample-images/` |
| `tests/` | #1208 | 80 pytest tests |

Run:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Test:

```bash
pip install -r requirements-dev.txt
python -m pytest
python evaluate_ocr.py
```

Requires the Tesseract program to be installed — see the main README.
