import os
import re
import json

BASE_DIR = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

# Only allow safe filenames
_SAFE_FILENAME = re.compile(r'^[a-zA-Z0-9_-]{4,64}\.json$')


def save_to_json(filename: str, data: dict):
    """
    Safely save intelligence output to processed JSON file.
    Validates filename to prevent path traversal.
    """
    if not _SAFE_FILENAME.match(filename):
        raise ValueError(f"Unsafe filename rejected: '{filename}'")

    file_path = os.path.join(PROCESSED_DIR, filename)

    # Resolve and verify containment
    resolved = os.path.realpath(file_path)
    if not resolved.startswith(os.path.realpath(PROCESSED_DIR)):
        raise ValueError(f"Path traversal detected: '{filename}'")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return file_path
