// Card #1207: check a chosen file in the browser BEFORE uploading it,
// so the user gets an instant, clear message. The backend repeats these
// checks (backend/validation.py) because a browser can't be fully trusted.

export const ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"];
const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"];
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB, same as the backend
const MAX_SIDE = 4000; // px; bigger photos are shrunk before upload
const MIN_SIDE = 50; // px; smaller images can't contain readable text

export const SUPPORTED_TEXT = "PNG, JPG, WEBP, BMP or TIFF";

function extensionOf(name) {
  const dot = name.lastIndexOf(".");
  return dot === -1 ? "" : name.slice(dot).toLowerCase();
}

export function formatSize(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Quick checks that only need the file name, type and size.
// Returns an error message, or "" if the file looks OK.
export function checkFile(file) {
  const ext = extensionOf(file.name);

  if (ext === ".heic" || ext === ".heif" || file.type === "image/heic") {
    return "iPhone HEIC photos are not supported yet. Please export the photo as JPG and try again.";
  }
  if (ext && !ALLOWED_EXTENSIONS.includes(ext)) {
    return `"${ext}" files are not supported. Please choose a ${SUPPORTED_TEXT} image.`;
  }
  // Some systems leave file.type empty; then the extension check above is enough.
  if (file.type && !ALLOWED_TYPES.includes(file.type)) {
    return `This file is not a supported image. Please choose a ${SUPPORTED_TEXT} image.`;
  }
  if (file.size === 0) {
    return "This file is empty. Please choose the photo again.";
  }
  return "";
}

// Opens the image to read its size, and shrinks very large photos to a JPEG.
// <img> and drawImage both apply the photo's EXIF orientation.
// Returns { file, width, height }; width/height are null if the browser can't show it (TIFF).
export async function prepareImage(file) {
  const url = URL.createObjectURL(file);
  try {
    const img = new Image();
    img.src = url;
    try {
      await img.decode();
    } catch {
      // Most browsers can't decode TIFF; send it as-is and let the backend check it.
      if (file.type === "image/tiff" || [".tif", ".tiff"].includes(extensionOf(file.name))) {
        return { file, width: null, height: null };
      }
      throw new Error("This file is damaged or is not really an image. Please try another photo.");
    }

    const width = img.naturalWidth;
    const height = img.naturalHeight;
    if (Math.min(width, height) < MIN_SIDE) {
      throw new Error(
        `This image is too small to read (${width}x${height} pixels). ` +
          "Please use a photo where the ingredient list is clearly visible."
      );
    }

    const scale = MAX_SIDE / Math.max(width, height);
    if (scale >= 1) return { file, width, height };

    const canvas = document.createElement("canvas");
    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff"; // JPEG has no transparency; keep it white, not black
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.9));
    if (!blob) throw new Error("Your browser could not process this image. Please try a lower-resolution photo.");
    const name = file.name.replace(/\.[^.]+$/, "") + ".jpg";
    return { file: new File([blob], name, { type: "image/jpeg" }), width: canvas.width, height: canvas.height };
  } finally {
    URL.revokeObjectURL(url);
  }
}

// Full check used by App.jsx. Returns { upload, info } or throws an Error with a friendly message.
export async function validateAndPrepare(file) {
  const problem = checkFile(file);
  if (problem) throw new Error(problem);

  const { file: upload, width, height } = await prepareImage(file);
  if (upload.size > MAX_FILE_SIZE) {
    throw new Error(`The image is too large (${formatSize(upload.size)}). The limit is 10 MB.`);
  }

  const info = {
    originalName: file.name,
    size: formatSize(upload.size),
    dimensions: width ? `${width}×${height}` : null,
    resized: upload !== file,
  };
  return { upload, info };
}
