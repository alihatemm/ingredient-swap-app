# Implementation Plan

## Stack
- Frontend: React
- Backend: FastAPI / Python
- OCR: ingredient text extraction
- Replacement data: Python dictionary or JSON

## Flow
1. User uploads an ingredient-list image.
2. Frontend sends the image to the backend.
3. Backend extracts the ingredient text.
4. Replacement logic finds healthier alternatives.
5. Frontend displays ingredient → replacement suggestions.

## Ownership
- Alejandro: Image Upload
- Mohamed: Ingredient Text Extraction
- Henry: Ingredient Replacement Logic
- Anthony: Display Swap Suggestions
- Ali: End-to-End Integration & Demo
