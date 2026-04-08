import sys
import time
from pathlib import Path

# Get the src directory relative to this script
current_dir = Path(__file__).resolve().parent  # ~/scripts
src_dir = current_dir.parent / "src"  # ~/src

# Add src to sys.path if it's not already there
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# import functionality from the llm directory
from llm import *


# --- EVALUATION METRIC ---
def calculate_relevance_score(query, response):
    """
    Simple Jaccard Similarity
    'Lexical Overlap' between the retrieved context and the generated answer.
    """
    q_set = set(query.lower().split())
    r_set = set(response.lower().split())
    if not q_set or not r_set:
        return 0.0
    intersection = q_set.intersection(r_set)
    union = q_set.union(r_set)
    score = len(intersection) / len(union)
    return score


def start_chat():
    # 1. Initialize chat and database
    assistant = QueriesAssistant()

    print("\n--- AI Assistant Ready (Type 'exit' to quit) ---")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        start_time = time.time()
        answer = assistant.run(user_input)

        # EVALUATION (Requirement: Benchmark Metric)
        latency = time.time() - start_time
        rel_score = calculate_relevance_score(user_input, answer)

        # 5. DISPLAY RESULTS
        print(f"\nHDB Sage: {answer}")
        print("-" * 30)
        print(f"METRICS:")
        print(f"- Latency: {latency:.2f}s")
        print(f"- Answer Relevance (Jaccard): {rel_score:.4f}")


if __name__ == "__main__":
    start_chat()
