import { useEffect, useState } from "react";
import { analyzeImage } from "./api.js";
import ImageUpload from "./components/ImageUpload.jsx";
import SwapResults from "./components/SwapResults.jsx";

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  // Create a temporary URL so the selected image can be previewed.
  useEffect(() => {
    if (!file) {
      setPreviewUrl("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function handleFileChange(newFile) {
    setError("");
    setResult(null);

    if (newFile && !newFile.type.startsWith("image/")) {
      setFile(null);
      setError("Please choose an image file (PNG or JPG).");
      return;
    }
    setFile(newFile);
  }

  async function handleAnalyze() {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzeImage(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header>
        <h1>Ingredient Swap</h1>
        <p className="muted">
          Upload a photo of a food label's ingredient list to get healthier replacement ideas.
        </p>
      </header>

      <ImageUpload
        file={file}
        previewUrl={previewUrl}
        onFileChange={handleFileChange}
        onAnalyze={handleAnalyze}
        loading={loading}
      />

      {loading && <p className="status">Reading the label… this can take a few seconds.</p>}
      {error && <p className="error">{error}</p>}
      {result && <SwapResults result={result} />}
    </main>
  );
}
