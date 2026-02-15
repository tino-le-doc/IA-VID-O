import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = OUTPUT_DIR / "scripts"
IMAGES_DIR = OUTPUT_DIR / "images"
VIDEOS_DIR = OUTPUT_DIR / "videos"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "pollinations")

# Ensure output directories exist
for d in [SCRIPTS_DIR, IMAGES_DIR, VIDEOS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
