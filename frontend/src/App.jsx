import { useEffect, useState } from "react";
import { analyzeImage } from "./api.js";
import ImageUpload from "./components/ImageUpload.jsx";
import SwapResults from "./components/SwapResults.jsx";
import { validateAndPrepare } from "./validation.js";

export default function App() {
  const [file, setFile] = useState(null); // the file that will be uploaded
  const [fileInfo, setFileInfo] = useState(null); // name, size, dimensions for display
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

  function clearFile() {
    setFile(null);
    setFileInfo(null);
    setResult(null);
    setError("");
  }

  async function handleFileChange(newFile) {
    clearFile(); // a rejected file stays cleared
    try {
      const { upload, info } = await validateAndPrepare(newFile);
      setFile(upload);
      setFileInfo(info);
    } catch (err) {
      setError(err.message);
    }
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
      <header className="app-header">
        <h1>Ingredient Swap</h1>
        <p className="muted">
          Upload a photo of a food label's ingredient list to get healthier replacement ideas.
        </p>
      </header>

      <div className="layout">
        <div className="left-column">
          <ImageUpload
            file={file}
            fileInfo={fileInfo}
            previewUrl={previewUrl}
            onFileChange={handleFileChange}
            onClear={clearFile}
            onAnalyze={handleAnalyze}
            loading={loading}
          />
        </div>

        <div className="right-column" aria-live="polite">
          {error && (
            <div className="error" role="alert">
              <strong>Something went wrong.</strong> {error}
            </div>
          )}

          {loading && (
            <section className="card status-card">
              <span className="spinner dark" aria-hidden="true" />
              <div>
                <strong>Reading the label…</strong>
                <p className="muted">
                  Straightening, cleaning up and reading the photo. This usually takes 1–3 seconds.
                </p>
              </div>
            </section>
          )}

          {result && <SwapResults result={result} />}

          {!result && !loading && !error && (
            <section className="card empty-state">
              <h2>Your results will appear here</h2>
              <p className="muted">
                Choose a photo of an ingredient list on the left, then press <em>Find healthier swaps</em>.
                Try one of the images in the <code>sample-images</code> folder.
              </p>
            </section>
          )}
        </div>
      </div>
    </main>
  );
}
