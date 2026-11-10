// Card: Image Upload (#1207)
// Pick or drag-and-drop an image; shows the name, size and a preview.

import { useState } from "react";
import { ALLOWED_EXTENSIONS, SUPPORTED_TEXT } from "../validation.js";

const ACCEPT = ["image/png", "image/jpeg", "image/webp", "image/bmp", "image/tiff", ...ALLOWED_EXTENSIONS].join(",");

export default function ImageUpload({ file, fileInfo, previewUrl, onFileChange, onClear, onAnalyze, loading }) {
  const [dragging, setDragging] = useState(false);

  function handleChange(event) {
    const selected = event.target.files[0];
    if (selected) onFileChange(selected);
    event.target.value = ""; // so picking the same file again (e.g. after a rejection) still fires
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    if (loading) return;
    const dropped = event.dataTransfer.files[0];
    if (dropped) onFileChange(dropped);
  }

  return (
    <section className="card upload-card">
      <h2>
        <span className="step">1</span> Upload an ingredient list
      </h2>

      <label
        className={`dropzone${dragging ? " dragging" : ""}${loading ? " disabled" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input type="file" accept={ACCEPT} onChange={handleChange} disabled={loading} />
        {previewUrl ? (
          <img className="preview" src={previewUrl} alt="Selected ingredient list" />
        ) : (
          <span className="dropzone-text">
            <strong>{file ? "Preview not available" : "Choose a photo"}</strong>
            {!file && " or drag it here"}
          </span>
        )}
      </label>
      <p className="hint">
        {SUPPORTED_TEXT} · up to 10 MB · a flat, well-lit photo of the ingredient list works best
      </p>

      {file && (
        <div className="file-info">
          <div>
            <strong className="filename">{fileInfo?.originalName || file.name}</strong>
            <span className="muted">
              {" "}
              · {fileInfo?.size}
              {fileInfo?.dimensions && ` · ${fileInfo.dimensions} px`}
              {fileInfo?.resized && " · resized for upload"}
            </span>
          </div>
          <button type="button" className="link-button" onClick={onClear} disabled={loading}>
            Remove
          </button>
        </div>
      )}

      <button className="analyze-button" onClick={onAnalyze} disabled={!file || loading}>
        {loading ? (
          <>
            <span className="spinner" aria-hidden="true" /> Analyzing…
          </>
        ) : (
          "Find healthier swaps"
        )}
      </button>
    </section>
  );
}
