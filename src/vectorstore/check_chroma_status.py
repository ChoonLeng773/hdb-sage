from pathlib import Path
import chromadb

PERSIST_DIR = "data/vectors"
CHROMA_COLLECTION_NAME = "my_knowledge_base"

persist_path = Path(__file__).resolve().parents[2] / PERSIST_DIR
client = chromadb.PersistentClient(path=persist_path)
col = client.list_collections()
print(col)  # should show your collection name

collection = client.get_collection(CHROMA_COLLECTION_NAME)
print(collection.count())  # should be > 0

# embeddings exist for my database -> search function to be updated
result = collection.get(limit=1, include=["embeddings"])
print(result["embeddings"])
