"""
This file runs the vector search for testing
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
    my_embedder = Embedder()
    my_db = VectorDatabaseSetup(persist_directory=PERSIST_DIR)

    hybrid = HybridSearcher(embedder=my_embedder, db=my_db)

    results = hybrid.search(VS_TC_1)
    print(type(results))


if __name__ == "__main__":
    run()
