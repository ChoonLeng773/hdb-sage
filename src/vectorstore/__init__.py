"""
This file exports these classes, functions and variables
"""

from .db_populate import DatabasePopulator
from .embedding import Embedder
from .db_setup import VectorDatabaseSetup
from .search import HybridSearcher
from .config import PERSIST_DIR, CHUNKS_DIR, VS_TC_1
from .load_data import load_json_chunks

__all__ = [
    "Embedder",
    "DatabasePopulator",
    "VectorDatabaseSetup",
    "HybridSearcher",
    "load_json_chunks",
    "CHUNKS_DIR",
    "PERSIST_DIR",
    "VS_TC_1",
]

# Optional: run code when package is imported
print("Database package has been loaded!")
