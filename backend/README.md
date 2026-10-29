# Backend (FastAPI)

| File | Card | What it does |
|---|---|---|
| `main.py` | End-to-End Integration | `GET /` health check, `POST /analyze` runs the full pipeline, CORS for `localhost:5173` |
| `ocr.py` | Ingredient Text Extraction | Opens the image, cleans it up (rotate, grayscale, upscale, contrast) and runs Tesseract |
| `ingredient_parser.py` | Ingredient Text Extraction | Keeps the text between "Ingredients:" and "Contains:", splits on commas/brackets, cleans each item |
| `replacements.py` | Ingredient Replacement Logic | Dictionary of swaps and whole-word matching |

Run:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Requires the Tesseract program to be installed — see the main README.
