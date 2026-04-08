"""
This file contains the configurations variables which are used within this dircetory
"""


class ChatConfig:
    """
    Class containing all of the configuration variables to be imported
    """

    MODEL_NAME = "mistral:7b"
    MODEL_TEMPERATURE = 0.2  # to adjust according to output quality
    SYSTEM_PROMPT = """
                    ## ROLE: You are an employee at the Housing Development Board of Singapore,
                    tasked with helping people with their home buying queries amidst the plethora
                    of policies and regulatory requirements on public housing. You will answer the
                    questions using informatin from the context only.
                    
                    ## RULES: Use only the context below to answer. If the answer is not in the
                    context, say you do not know, do not make up any information.
                    
                    ## CONTEXT: {context}
                    ## QUESTION: {question}
                    ANSWER:
                    """
    QUERY_PROMPT = """
                    Rewrite the user query to improve semantic search retrieval.
                    Add relevant keywords and context, but keep it concise.

                    User query: {query}
                    Rewritten query:
                """
