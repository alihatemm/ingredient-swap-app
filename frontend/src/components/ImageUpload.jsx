// Card: Image Upload
// Lets the user pick an image, shows its name and a preview.

export default function ImageUpload({ file, previewUrl, onFileChange, onAnalyze, loading }) {
  function handleChange(event) {
    const selected = event.target.files[0];
    onFileChange(selected || null);
    event.target.value = ""; // so picking the same file again (e.g. after a rejection) still fires
  }

  return (
    <section className="card">
      <h2>1. Upload an ingredient list</h2>

      <label className="file-picker">
        <input type="file" accept="image/png,image/jpeg,image/webp,image/bmp,image/tiff" onChange={handleChange} disabled={loading} />
        <span>{file ? "Choose a different image" : "Choose an image"}</span>
      </label>

      {file && (
        <p className="filename">
          Selected: <strong>{file.name}</strong>
        </p>
      )}

      {previewUrl && <img className="preview" src={previewUrl} alt="Selected ingredient list" />}

      <button className="analyze-button" onClick={onAnalyze} disabled={!file || loading}>
        {loading ? "Analyzing…" : "Find healthier swaps"}
      </button>
    </section>
  );
}
