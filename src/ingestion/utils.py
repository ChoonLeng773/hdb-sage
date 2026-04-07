"""
This module supplies the other modules within ingestion directory with common functionality
1. save file function with relative file paths
2.
"""

import re
import json
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """
    Lowers casing for file naming
    Removes weird characters which can cause issues for saving the file
    replaces spacing with underscore
    """
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s]+", "_", name)
    return name


def save_data(path_from_root: str, chunk_id: str, data: dict[str, str]):
    """
    Takes the name of the section as well as the dictionary
    Creates the json file containing {subsections : html}
    Saved to ~/data/raw to be chunked
    """
    filename = sanitize_filename(chunk_id) + ".json"
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / path_from_root
    output_dir.mkdir(parents=True, exist_ok=True)

    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:  # overwrites existing files
        json.dump(data, f, indent=2, ensure_ascii=False)
