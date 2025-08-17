import os



# Get backend root (one level up from app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")
HISTORICAL_DIR = os.path.join(STORAGE_DIR, "historical")
DOCUMENTS_DIR = os.path.join(STORAGE_DIR, "documents")
OUTPUT_DIR = os.path.join(STORAGE_DIR, "output")

# Ensure folders exist
os.makedirs(HISTORICAL_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODE = os.getenv("MODE", "auto")  # auto, offline, online

# How many top sections/snippets to show per query
TOP_SECTIONS_COUNT = int(os.getenv("TOP_SECTIONS_COUNT", "6"))

# TTS provider: 'google' or 'local'
TTS_PROVIDER = (os.getenv("TTS_PROVIDER") or "google").lower()
