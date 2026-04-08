"""
This file exports these classes, functions and variables within the llm directory
"""

from .chat_config import ChatConfig
from .chat_generator import QueriesAssistant

__all__ = [
    "ChatConfig",
    "QueriesAssistant",
]

# Optional: run code when package is imported
print("Chat package has been loaded!")
