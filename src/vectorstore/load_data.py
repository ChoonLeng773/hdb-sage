"""
This file contains methods used to load json data from a specified directory.
"""

import json
from pathlib import Path


def load_json_chunks(directory_path: str) -> list[dict]:
    """
    Scans a directory for JSON files and loads them into a list of dictionaries.
    Maps "data" key to "text" to match our previous pipeline logic. (might not be necessary)
    """
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / directory_path
    all_chunks = []

    # Check if the directory actually exists
    if not path.exists():
        print(f"Error: The directory {path} does not exist.")
        return []

    print(f"Scanning for JSON chunks in: {path}...")

    # Iterate over all files ending in .json
    for json_file in path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = json.load(f)

                # If your JSON is a single object: {"data": "..", "url": ".."}
                if isinstance(content, dict):
                    # We map "data" to "text" so it fits our Embedder seamlessly
                    formatted_chunk = {
                        "text": content.get("data", ""),
                        "source": content.get("url", "unknown"),
                        "category": content.get("category", "general"),
                    }
                    all_chunks.append(formatted_chunk)

        except Exception as e:
            print(f"Could not read file {json_file.name}: {e}")

    print(f"Successfully loaded {len(all_chunks)} chunks.")
    return all_chunks
