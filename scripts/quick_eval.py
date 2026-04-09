# from ragas import evaluate, EvaluationDataset
# from ragas.metrics import faithfulness, context_precision
# from langchain_ollama import ChatOllama

# import sys
# from pathlib import Path

# current_dir = Path(__file__).resolve().parent  # ~/scripts
# src_dir = current_dir.parent / "src"  # ~/src

# if str(src_dir) not in sys.path:
#     sys.path.insert(0, str(src_dir))

# from llm import *

# # 1. llm evaluator : gemma4:e4b new, or use any LLM that is larger than the generator
# evaluator_llm = ChatOllama(model="mistral:7b")

# # 2. Prepare the Evaluation Dataset
# # You need to run your chat loop once and store the results in this list format
# data = {
#     "question": [
#         "What is the income ceiling for singles for them to be eligible for the deferred income assessment?"
#     ],
#     "answer": ["The income ceiling for the Singles is $7,000."],  # supposed response
#     "contexts": [
#         ["Singles Grant eligibility: Income must not exceed $7,000..."]
#     ],  # build from hdb's website
#     "ground_truth": ["$7,000"],  # use larger llms to create a list of these from chunks
# }

# dataset = EvaluationDataset.from_list(
#     [
#         {
#             "user_input": data["question"][0],
#             "response": data["answer"][0],
#             "retrieved_contexts": data["contexts"][0],
#             "reference": data["ground_truth"][0],
#         }
#     ]
# )

# # 3. Run Evaluation
# results = evaluate(
#     dataset=dataset, metrics=[faithfulness, context_precision], llm=evaluator_llm
# )

# print(results)
