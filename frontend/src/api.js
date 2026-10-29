// Talks to the FastAPI backend.
// Change VITE_API_URL in a .env file if the backend runs somewhere else.
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function analyzeImage(file) {
  const formData = new FormData();
  formData.append("file", file); // field name must match the FastAPI parameter

  let response;
  try {
    response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error(
      `Could not reach the backend at ${API_URL}. Is uvicorn running?`
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    // FastAPI sends errors as { detail: "message" } (or a list for validation errors).
    const detail =
      typeof data.detail === "string"
        ? data.detail
        : "Something went wrong while analyzing the image.";
    throw new Error(detail);
  }

  return data;
}
