from langchain_huggingface import HuggingFaceEmbeddings

def get_embeddings_model(model_name: str = "BAAI/bge-m3") -> HuggingFaceEmbeddings:
    
    return HuggingFaceEmbeddings(
        model_name=model_name, 
        encode_kwargs={"normalize_embeddings": True} # means: when encoding, call the underlying library with normalize_embeddings=True
    ) 