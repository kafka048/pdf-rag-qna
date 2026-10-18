from loader import load_pdf
from embeddings import get_embeddings_model
from vector_store import get_vector_store, is_empty
from splitter import split_documents_recursive, split_texts_semantic

from _collections_abc import Callable
from langchain_chroma import Chroma
from langchain_core.documents import Document


file_path = "data/nandpur_water_security_handbook.pdf"
recursive_collection_name = "recursive_handbook"
semantic_collection_name = "semantic_handbook"

docs = load_pdf(file_path)
emb_model = get_embeddings_model(model_name="BAAI/bge-m3")

print(len(docs))

def ingest_documents(collection_name: str, make_chunks: Callable[[], list[Document]]) -> Chroma:
    # open the collection by its name
    store = get_vector_store(embedding_model=emb_model, collection_name=collection_name)

    # guard: if it already has chunks, do not add the same chunks again
    if not is_empty(store):
        print(f"{collection_name}: already built, skipping")
        return store
    
    chunks = make_chunks()

    store.add_documents(chunks)
    print(f"{collection_name}: added {len(chunks)} chunks")
    return store



recursive_store = ingest_documents(recursive_collection_name, lambda: split_documents_recursive(docs))
semantic_store = ingest_documents(semantic_collection_name, lambda: split_texts_semantic(docs, emb_model, "percentile", 80))


question: str = "how much is the rainwater subsidy?"
for name, store in [(recursive_collection_name, recursive_store), (semantic_collection_name, semantic_store)]:
    print(f"\n{name}")
    for doc, score in store.similarity_search_with_score(question, k=4):
        print(f"score: {score:.3f} | page_label={doc.metadata['page_label']} | {doc.page_content}")