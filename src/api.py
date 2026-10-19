from fastapi import FastAPI  
from pydantic import BaseModel 

from embeddings import get_embeddings_model 
from vector_store import get_vector_store  
from generator import get_llm  
from pipeline import answer_question  

COLLECTION_NAME = "recursive_handbook"  
MODEL_NAME = "qwen3:8b"  
K = 4  


class AskRequest(BaseModel):  
    question: str  


class AskResponse(BaseModel): 
    answer: str  
    sources: list[str]  

app = FastAPI(title="PDF RAG Q&A")  

emb = get_embeddings_model(model_name="BAAI/bge-m3")  
store = get_vector_store(emb, COLLECTION_NAME)  
llm = get_llm(MODEL_NAME)  


@app.post("/ask", response_model=AskResponse) 
def ask(request: AskRequest) -> AskResponse:  
    answer, pages = answer_question(store, llm, request.question, K)  
    return AskResponse(answer=answer, sources=pages)  