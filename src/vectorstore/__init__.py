"""
This file exports these classes, functions and variables
"""

from .db_populate import DatabasePopulator
from .embedding import Embedder
from .db_setup import VectorDatabaseSetup
from .config import PERSIST_DIR, CHUNKS_DIR
from .load_data import load_json_chunks

__all__ = [
    "Embedder",
    "DatabasePopulator",
    "VectorDatabaseSetup",
    "load_json_chunks",
    "CHUNKS_DIR",
    "PERSIST_DIR",
]

# Optional: run code when package is imported
print("filename package has been loaded!")
