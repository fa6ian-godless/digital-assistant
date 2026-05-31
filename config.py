import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

UPLOAD_DIR = BASE_DIR / "uploads"
TRANSCRIPT_DIR = BASE_DIR / "transcripts"
RESULTS_DIR = BASE_DIR / "results"

UPLOAD_DIR.mkdir(exist_ok = True)
TRANSCRIPT_DIR.mkdir(exist_ok = True)
RESULTS_DIR.mkdir(exist_ok = True)

WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

OLLAMA_MODEL = "llama3"
OLLAMA_HOST = "http://localhost:11434"