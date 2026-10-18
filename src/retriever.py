from langchain_chroma import Chroma
from langchain_core.documents import Document


def retrieve_chunks(store: Chroma, query: str, k: int = 3) -> list[tuple[Document, float]]:

    return store.similarity_search_with_score(query, k=k) # returns a list of tuples containing the chunk document and its similarity score.


def show_results(results: list[tuple[Document, float]], preview: int | None = None) -> None:
    for rank, (doc, score) in enumerate(results, start=1):
        print(f"\n#{rank} | score {score:.3f} | page_label={doc.metadata['page_label']} | {len(doc.page_content)} chars")
        # preview=None prints the whole chunk, preview=200 prints only the first 200 characters
        print(doc.page_content if preview is None else doc.page_content[:preview])


