from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

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
# print(result["embeddings"])

query = """I am a fresh grad who just started working, and i would like to buy a house.
What schemes can be helpful to me and my girlfriend?"""

model = SentenceTransformer("all-MiniLM-L6-v2")
query_vector = model.encode([query]).tolist()
print(len(query_vector))
query_answer = collection.query(
    query_embeddings=query_vector[0],
    n_results=3,
    include=["documents", "embeddings", "metadatas"],
)
print(query_answer)
