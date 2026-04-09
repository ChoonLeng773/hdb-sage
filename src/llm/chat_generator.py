# import os
import sys
from pathlib import Path

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# from langchain_core.runnables import RunnablePassthrough

llm_dir = Path(__file__).resolve().parent  # ~/llm
if str(llm_dir) not in sys.path:
    sys.path.insert(0, str(llm_dir))

from chat_config import ChatConfig

# Get the ingestion directory relative to this script
src_dir = Path(__file__).resolve().parents[1]  # ~/src

# Add src to sys.path if it's not already there
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from vectorstore import *  # for the database functions

MODEL_NAME = ChatConfig.MODEL_NAME
MODEL_TEMPERATURE = ChatConfig.MODEL_TEMPERATURE
SYSTEM_PROMPT = ChatConfig.SYSTEM_PROMPT
OLLAMA_HOST = ChatConfig.OLLAMA_HOST


class QueriesAssistant:
    """
    This class handles the queries
    """

    def __init__(self, model_name: str = MODEL_NAME):
        """
        Requirement: 7B or lower model.
        I like Mistral-7B, but the newer models use lesser resources despite having more parameters
        due to their architecure.
        ministral-3:8b is also a good choice
        """
        self.llm = ChatOllama(
            model=model_name,
            temperature=MODEL_TEMPERATURE,
            base_url=OLLAMA_HOST,
        )
        self.template = SYSTEM_PROMPT
        self.prompt = ChatPromptTemplate.from_template(self.template)
        self.output_parser = StrOutputParser()

        self.embedder = Embedder()
        self.vec_db = VectorDatabaseSetup(
            persist_directory=Path(__file__).resolve().parents[2]
            / PERSIST_DIR  # ~/data/vector
        )
        self.query_engine = HybridSearcher(embedder=self.embedder, db=self.vec_db)

    def format_docs(self, docs: dict):
        """Helper to extract ALL retrieved chunks text data (documents: [...]) from ChromaDB query"""
        return "\n\n".join(docs.get("documents", []))

    def run(self, query: str) -> str:
        """
        Returns only a string response when called.
        Alternative method of query -> call LLM twice,
        first to clean up query, next to generate response
        """
        query_chunks = self.query_engine.search(query)  #
        # print("what is this strange object", query_chunks)
        chain = (
            {
                "context": lambda x: self.format_docs(x["docs"]),
                "question": lambda x: x["question"],
            }
            | self.prompt
            | self.llm
            | self.output_parser
        )
        try:
            answers = chain.invoke({"question": query, "docs": query_chunks})
        except Exception as _:
            print(f"Model might not be installed. Try: ollama pull {MODEL_NAME}")
            answers = "Error: model invocation failed."

        # Single turn execution only
        return answers


# testing this function
# qa_monster = QueriesAssistant("ministral-3:8b")
# answer_me = qa_monster.run(VS_TC_1)
# print(answer_me)
