import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment in a deterministic order:
# 1) project root .env (preferred)
# 2) backend/.env as fallback for local-only setups
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _BACKEND_DIR.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)
load_dotenv(_BACKEND_DIR / ".env", override=False)


def get_gemini_api_key() -> str:
	return os.getenv("GEMINI_API_KEY", "").strip()


def get_gptzero_api_key() -> str:
	return os.getenv("GPTZERO_API_KEY", "").strip()


def get_max_file_size_mb() -> int:
	raw_value = os.getenv("MAX_FILE_SIZE_MB", "10").strip()
	try:
		parsed = int(raw_value)
		return parsed if parsed > 0 else 10
	except ValueError:
		return 10
