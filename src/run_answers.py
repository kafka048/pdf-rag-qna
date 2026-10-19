from embeddings import get_embeddings_model  # loads bge-m3
from vector_store import get_vector_store  # opens a saved Chroma collection
from generator import get_llm  # connects to the Ollama model
from pipeline import answer_question  # retrieve, then generate, returns (answer, pages)
from questions import QUESTIONS  # the 10 questions with expected answers

MODEL_NAME = "qwen3:8b"  # change to "llama3.1:8b" to run the other model
K = 4  # chunks retrieved per question

COLLECTIONS = {  # which Chroma collection belongs to which store
    "recursive": "recursive_handbook",
    "semantic": "semantic_handbook",
}

emb = get_embeddings_model(model_name="BAAI/bge-m3")  # load the embedding model once
llm = get_llm(MODEL_NAME)  # connect to the model once

for store_name, collection_name in COLLECTIONS.items():  # go through both stores, one after the other
    store = get_vector_store(emb, collection_name)  # open this store
    print(f"\n===== {store_name.upper()} | {MODEL_NAME} =====")  # banner so you know which store the answers below belong to
    for number, q in enumerate(QUESTIONS, start=1):  # go through the questions, numbering from 1
        question = str(q["question"])  # str() because the dict allows None
        answer, pages = answer_question(store, llm, question, K)  # retrieve and generate
        abstained = "could not find" in answer.lower()  # True if the model used the "I could not find this" line
        print(f"\nQ{number}: {question}")  # show the question
        print(f"   expected:  {q['expected']}")  # what a correct answer must contain
        print(f"   answer:    {answer}")  # what the model said
        print(f"   pages:     {pages} | abstained: {abstained}")  # where the chunks came from, and whether it declined
        