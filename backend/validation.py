"""
Upload validation (Sprint B #1207).

Every check returns a message a normal user can understand. The checks run in
order from cheapest to most expensive:

    1. file name / extension        (e.g. .pdf, .heic)
    2. content type sent by the browser
    3. empty file / too big
    4. real format from the file's bytes (a .png that is really a .txt)
    5. image size in pixels         (too small to read, or too many pixels)
"""

import io
from pathlib import Path

from PIL import Image, UnidentifiedImageError

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"}
# Real formats as Pillow names them. Some phone cameras save JPEGs that Pillow reads as MPO.
ALLOWED_FORMATS = {"PNG", "JPEG", "MPO", "WEBP", "BMP", "TIFF"}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MIN_SIDE = 50  # pixels; anything smaller cannot contain readable label text

SUPPORTED_LIST = "PNG, JPG, WEBP, BMP or TIFF"
UNSUPPORTED_TYPE_MESSAGE = f"Unsupported file type. Please upload a {SUPPORTED_LIST} image."
HEIC_MESSAGE = (
    "iPhone HEIC photos are not supported yet. Please export the photo as JPG "
    "(or set Camera > Formats to 'Most Compatible') and try again."
)


class UploadError(Exception):
    """A problem with the uploaded file. status is the HTTP status code to return."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def check_file_name(filename):
    extension = Path(filename or "").suffix.lower()
    if extension in {".heic", ".heif"}:
        raise UploadError(HEIC_MESSAGE)
    if not extension:
        return  # some apps send pasted images without a name; the other checks still run
    if extension not in ALLOWED_EXTENSIONS:
        raise UploadError(f"'{extension}' files are not supported. Please upload a {SUPPORTED_LIST} image.")


def check_content_type(content_type):
    if content_type in {"image/heic", "image/heif"}:
        raise UploadError(HEIC_MESSAGE)
    if content_type not in ALLOWED_TYPES:
        raise UploadError(UNSUPPORTED_TYPE_MESSAGE)


def check_size(image_bytes):
    if not image_bytes:
        raise UploadError("The uploaded file is empty. Please choose the photo again.")
    if len(image_bytes) > MAX_FILE_SIZE:
        size_mb = len(image_bytes) / (1024 * 1024)
        raise UploadError(f"The image is too large ({size_mb:.1f} MB). The limit is 10 MB.")


def check_image_contents(image_bytes):
    """Open the image header to check its real format and its size in pixels."""
    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            real_format = image.format
            width, height = image.size
    except Image.DecompressionBombError:
        raise UploadError(
            "The image resolution is too large to process. Please upload a lower-resolution photo.", 422
        )
    except (UnidentifiedImageError, OSError):
        raise UploadError("The file is damaged or is not really an image. Please try another photo.", 422)

    if real_format not in ALLOWED_FORMATS:
        raise UploadError(UNSUPPORTED_TYPE_MESSAGE)
    if min(width, height) < MIN_SIDE:
        raise UploadError(
            f"The image is too small to read ({width}x{height} pixels). "
            "Please upload a photo where the ingredient list is clearly visible.",
            422,
        )


def validate_upload(filename, content_type, image_bytes):
    """Run every check. Raises UploadError with a friendly message if one fails."""
    check_file_name(filename)
    check_content_type(content_type)
    check_size(image_bytes)
    check_image_contents(image_bytes)
