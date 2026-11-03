import { useEffect, useState } from "react";
import { analyzeImage } from "./api.js";
import ImageUpload from "./components/ImageUpload.jsx";
import SwapResults from "./components/SwapResults.jsx";

// Same types and size limit as the backend (backend/main.py).
const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
const MAX_SIDE = 4000; // px; bigger photos are shrunk before upload

// Shrink images whose longest side is over MAX_SIDE to a JPEG, keeping aspect ratio.
// <img> and drawImage both apply the photo's EXIF orientation.
async function shrinkImage(file) {
  const url = URL.createObjectURL(file);
  try {
    const img = new Image();
    img.src = url;
    try {
      await img.decode();
    } catch (err) {
      // Most browsers can't decode TIFF; send it as-is and let the backend check it.
      if (file.type === "image/tiff") return file;
      throw err;
    }

    const scale = MAX_SIDE / Math.max(img.naturalWidth, img.naturalHeight);
    if (scale >= 1) return file;

    const canvas = document.createElement("canvas");
    canvas.width = Math.round(img.naturalWidth * scale);
    canvas.height = Math.round(img.naturalHeight * scale);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff"; // JPEG has no transparency; keep it white, not black
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.9));
    if (!blob) throw new Error("Could not encode the resized image.");
    const name = file.name.replace(/\.[^.]+$/, "") + ".jpg";
    return new File([blob], name, { type: "image/jpeg" });
  } finally {
    URL.revokeObjectURL(url);
  }
}

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

  async function handleFileChange(newFile) {
    setError("");
    setResult(null);
    setFile(null); // a rejected file stays cleared
    if (!newFile) return;

    if (!ALLOWED_TYPES.includes(newFile.type)) {
      setError("Please choose a PNG, JPG, WEBP, BMP or TIFF image.");
      return;
    }

    let upload;
    try {
      upload = await shrinkImage(newFile);
    } catch {
      setError("Your browser could not process this image. Please try a lower-resolution photo.");
      return;
    }

    if (upload.size > MAX_FILE_SIZE) {
      setError("The image is too large (max 10 MB). Please choose a smaller file.");
      return;
    }
    setFile(upload);
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
