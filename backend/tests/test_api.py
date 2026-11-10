"""
#1207 upload validation and #1208 end-to-end API checks.
Uses FastAPI's TestClient (needs httpx: pip install -r requirements-dev.txt).
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from conftest import SAMPLES
from main import app

client = TestClient(app)


def image_bytes(fmt="PNG", size=(400, 300), color="white"):
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, fmt)
    return buffer.getvalue()


def post(name, data, content_type):
    return client.post("/analyze", files={"file": (name, data, content_type)})


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["swaps_available"] >= 48


def test_cors_allows_vite_dev_server():
    for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
        response = client.options("/analyze", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
        })
        assert response.headers["access-control-allow-origin"] == origin


@pytest.mark.parametrize("name, content_type", [
    ("cookie-label.png", "image/png"),
    ("cereal-rotated.jpg", "image/jpeg"),
    ("granola-bar-dark.jpg", "image/jpeg"),
    ("soda-shadow-noisy.jpg", "image/jpeg"),
    ("pizza-white-on-dark.png", "image/png"),
])
def test_analyze_sample_images(name, content_type):
    response = post(name, (SAMPLES / name).read_bytes(), content_type)
    assert response.status_code == 200, response.text
    body = response.json()
    # Sprint A fields are unchanged
    assert body["filename"] == name
    assert body["extracted_text"]
    assert body["ingredients"]
    assert body["suggestions"]
    # Sprint B fields
    assert set(body["ocr"]) == {"method", "confidence", "rotated"}
    assert isinstance(body["corrections"], list)


@pytest.mark.parametrize("fmt, content_type, name", [
    ("JPEG", "image/jpeg", "label.jpeg"),
    ("WEBP", "image/webp", "label.webp"),
    ("BMP", "image/bmp", "label.bmp"),
    ("TIFF", "image/tiff", "label.tif"),
])
def test_other_supported_formats_upload(fmt, content_type, name):
    original = Image.open(SAMPLES / "cookie-label.png").convert("RGB")
    buffer = io.BytesIO()
    original.save(buffer, fmt)
    response = post(name, buffer.getvalue(), content_type)
    assert response.status_code == 200, response.text
    assert response.json()["suggestions"]


@pytest.mark.parametrize("name, data, content_type, status, message_part", [
    ("notes.txt", b"hello", "text/plain", 400, "'.txt' files are not supported"),
    ("label.pdf", b"%PDF-1.4", "application/pdf", 400, "'.pdf' files are not supported"),
    ("IMG_0001.HEIC", b"....", "image/heic", 400, "HEIC"),
    ("label.png", b"hello", "text/plain", 400, "Unsupported file type"),
    ("empty.png", b"", "image/png", 400, "empty"),
    ("fake.png", b"this is not an image", "image/png", 422, "damaged or is not really an image"),
    ("tiny.png", image_bytes(size=(30, 20)), "image/png", 422, "too small to read"),
    ("blank.png", image_bytes(), "image/png", 422, "No text was found"),
])
def test_bad_uploads_fail_cleanly(name, data, content_type, status, message_part):
    response = post(name, data, content_type)
    assert response.status_code == status, response.text
    assert message_part in response.json()["detail"]


def test_gif_renamed_to_png_is_rejected():
    gif = image_bytes(fmt="GIF")
    response = post("sneaky.png", gif, "image/png")
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_file_too_large():
    response = post("huge.png", b"0" * (10 * 1024 * 1024 + 1), "image/png")
    assert response.status_code == 400
    assert "too large" in response.json()["detail"]


def test_missing_file_field():
    response = client.post("/analyze")
    assert response.status_code == 422
