"""
Settings for vector database creation and operation
"""

# Folder structure
PERSIST_DIR = "data/vectors"
CHUNKS_DIR = "data/chunks"

# Embedding
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Vector Database
CHROMA_COLLECTION_NAME = "my_knowledge_base"
NUM_QUERY_RESULTS = 5

# Vector Testing
VS_TC_1 = """
    I am a fresh grad who just started working, and i would like to buy a house. What schemes
    can be helpful to me and my girlfriend?
"""
