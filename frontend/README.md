# Frontend (React + Vite)

| File | Card | What it does |
|---|---|---|
| `src/components/ImageUpload.jsx` | #1207 Upload | Click or drag & drop, preview, file name/size/dimensions, Remove, analyze button with spinner |
| `src/validation.js` | #1207 Validation | Checks the file in the browser before upload (type, HEIC, empty, damaged, too small, too big) and shrinks photos over 4000 px |
| `src/components/SwapResults.jsx` | #1206 Results | Summary counts, OCR details and warnings, "Instead of → Try" swaps with category badges, highlighted ingredients, raw OCR text |
| `src/App.jsx` | #1206 / Integration | Two-column layout; state for file, loading, error and result |
| `src/App.css` | #1206 | Styles; one column below 860 px |
| `src/api.js` | Integration | Sends the image to `POST /analyze` and turns errors into readable messages |

Run (backend must be running on port 8000):

```bash
npm install
npm run dev
```

Then open http://localhost:5173.
