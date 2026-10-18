from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIRECTORY = "chroma_persist_db"

def get_vector_store(embedding_model: HuggingFaceEmbeddings, collection_name: str, persist_directory: str = PERSIST_DIRECTORY) -> Chroma:
    # One function is enough to create multiple stores that will vary on the collection name.
    
    return Chroma(persist_directory=persist_directory, collection_name=collection_name, embedding_function=embedding_model)



def is_empty(store: Chroma) -> bool:
    # get() fetches stored items by position, with no similarity search.
    # limit=1 means "at most one item": we only need to know if anything exists.
    # It returns a dict like {"ids": [...], "documents": [...], "metadatas": [...]}
    result = store.get(limit=1)

    # "ids" holds one id per stored chunk, so it is [] when the collection is empty.
    ids = result["ids"]

    # An empty list counts as False in Python, so `not ids` is True only when empty.
    return not ids