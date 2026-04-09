import sys
from pathlib import Path

# Get the src directory relative to this script
current_dir = Path(__file__).resolve().parent  # ~/scripts
src_dir = current_dir.parent / "src"  # ~/src

# Add src to sys.path if it's not already there
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now we can import from src/ingestion
from ingestion import load_hdb_data, generate_chunks


def run():
    """Run ingestion pipeline to generate chunks."""
    load_hdb_data()
    generate_chunks()

    print("Chunk generation complete!")


if __name__ == "__main__":
    run()
