# Frontend (React + Vite)

| File | Card | What it does |
|---|---|---|
| `src/components/ImageUpload.jsx` | Image Upload | File picker, filename, image preview, analyze button |
| `src/api.js` | End-to-End Integration | Sends the image to `POST /analyze` and turns errors into readable messages |
| `src/App.jsx` | End-to-End Integration | Holds the state: selected file, loading, error, result |
| `src/components/SwapResults.jsx` | Display Swap Suggestions | Shows original → replacement, the ingredient list and the raw OCR text |

Run (backend must be running on port 8000):

```bash
npm install
npm run dev
```

Then open http://localhost:5173.
