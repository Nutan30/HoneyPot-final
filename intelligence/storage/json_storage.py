import os
import json

BASE_DIR = os.path.dirname(__file__)
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)


def save_to_json(filename: str, data: dict):
    """
    Safely save intelligence output to processed JSON file.
    """

    file_path = os.path.join(PROCESSED_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ JSON write completed:", file_path)
    return file_path
