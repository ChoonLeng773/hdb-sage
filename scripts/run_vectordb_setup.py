"""
This file runs the functions required to setup the vector database in ~/data/vectors
from chunks in ~/data/raw.
Note: It deletes all of the previous data in the vector database.
"""

import sys
from pathlib import Path

# Get the src directory relative to this script
current_dir = Path(__file__).resolve().parent  # ~/scripts
src_dir = current_dir.parent / "src"  # ~/src

# Add src to sys.path if it's not already there
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from vectorstore import *


def run():
    """Set up vector database and populate it with embeddings."""

    # 1️⃣ Load data chunks
    print(f"Loading data from: {CHUNKS_DIR}")
    raw_data = load_json_chunks(CHUNKS_DIR)

    # 2️⃣ Initialize embedder and vector database
    print("Initializing embedder and vector database...")
    my_embedder = Embedder()  # Defaults to all-MiniLM-L6-v2

    # Use absolute path relative to this script for persistence
    persist_path = Path(__file__).resolve().parents[2] / PERSIST_DIR
    persist_path.mkdir(parents=True, exist_ok=True)
    my_db = VectorDatabaseSetup(
        persist_directory=str(persist_path), reset_db=True
    )  # erase previous data at setup

    # 3️⃣ Start orchestrator
    populator = DatabasePopulator(embedder=my_embedder, db=my_db)

    # 4️⃣ Process data and upload embeddings
    print("Processing and uploading data to vector database...")
    populator.process_and_upload(raw_data)

    print("Vector database setup complete!")


if __name__ == "__main__":
    run()
