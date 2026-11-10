import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
SAMPLES = BACKEND.parent / "sample-images"

# Let tests "import main", "import ocr", ... like the app does.
sys.path.insert(0, str(BACKEND))
