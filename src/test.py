from loader import load_pdf
from embeddings import get_embeddings_model
from vector_store import get_vector_store
from retriever import retrieve_chunks
from generator import get_llm
from pipeline import answer_question
from questions import QUESTIONS, FACTS


## 1. LOADER

file_path = ""

documents = load_pdf(file_path)


## 2. SETUP: EMBEDDING MODEL AND BOTH STORES

recursive_collection_name = "recursive_handbook"
semantic_collection_name = "semantic_handbook"

emb_model = get_embeddings_model(model_name="BAAI/bge-m3")
stores = {
    "recursive": get_vector_store(emb_model, recursive_collection_name),
    "semantic": get_vector_store(emb_model, semantic_collection_name),
}

K = 4


## 3. ONE QUESTION THROUGH THE FULL PIPELINE

question = "What is the fluoride limit?"

llm = get_llm()

for name, store in stores.items():
    answer, pages = answer_question(store, llm, question)
    print(f"\n=== {name} ===")
    print(answer)
    print("pages retrieved:", pages)


## 4. PAGE-LEVEL RETRIEVAL EVALUATION

hits = {name: 0 for name in stores}
answerable = 0

for number, q in enumerate(QUESTIONS, start=1):
    eval_question = str(q["question"])
    answer_page = q["page"]
    if answer_page is not None:
        answerable += 1
    print(f"\nQ{number}: {eval_question}")
    print(f"   answer page: {answer_page}")
    for name, store in stores.items():
        results = retrieve_chunks(store, eval_question, K)
        pages = [doc.metadata["page_label"] for doc, _score in results]
        top_score = results[0][1]
        if answer_page is None:
            verdict = "no answer exists, compare this score with the others"
        elif answer_page in pages:
            verdict = f"HIT at rank {pages.index(answer_page) + 1}"
            hits[name] += 1
        else:
            verdict = "MISS"
        print(f"   {name:9s} top score {top_score:.3f} | pages {pages} | {verdict}")

print("\nSUMMARY")
for name in stores:
    print(f"   {name:9s} {hits[name]}/{answerable} answer pages retrieved")


## 5. STRICT CHECK

def normalize(text: str) -> str:
    return " ".join(text.split()).lower()

strict_hits = {name: 0 for name in stores}
strict_top1 = {name: 0 for name in stores}
strict_total = 0

for number, q in enumerate(QUESTIONS, start=1):
    facts = FACTS.get(number)
    if facts is None:
        continue
    strict_total += 1
    eval_question = str(q["question"])
    print(f"\nQ{number}: {eval_question}")
    print(f"   facts that must appear together: {facts}")
    for name, store in stores.items():
        results = retrieve_chunks(store, eval_question, K)
        found_rank = None
        for rank, (doc, _score) in enumerate(results, start=1):
            text = normalize(doc.page_content)
            if all(normalize(f) in text for f in facts):
                found_rank = rank
                break
        if found_rank is None:
            verdict = "NOT FOUND in any retrieved chunk"
        else:
            verdict = f"found in the chunk at rank {found_rank}"
            strict_hits[name] += 1
            if found_rank == 1:
                strict_top1[name] += 1
        print(f"   {name:9s} {verdict}")

print("\nSTRICT SUMMARY")
for name in stores:
    print(f"   {name:9s} in top {K}: {strict_hits[name]}/{strict_total} | at rank 1: {strict_top1[name]}/{strict_total}")


## 6. DEBUG: Q8 ON THE SEMANTIC STORE

debug_question = "By how much did the Karanpur pilot reduce tanker dependence?"
for rank, (doc, _score) in enumerate(retrieve_chunks(stores["semantic"], debug_question, K), start=1):
    text = normalize(doc.page_content)
    print(f"\n#{rank} | page {doc.metadata['page_label']} | has '31 percent': {'31 percent' in text} | has 'karanpur': {'karanpur' in text}")
    print(doc.page_content)