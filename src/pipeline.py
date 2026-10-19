from langchain_chroma import Chroma  
from langchain_ollama import OllamaLLM  

from generator import generate_answer  
from retriever import retrieve_chunks

def answer_question(store: Chroma, llm: OllamaLLM, question: str, k: int = 3) -> tuple[str, list[str]]:
    results = retrieve_chunks(store, question, k=k) # retrieve the top k (chunk, score) pairs for this question
    answer = generate_answer(llm, question, results) # the model answers using only those chunks
    
    pages: list[str] = [] # will hold each page number once

    for doc, _score in results:  # go through every retrieved chunk
        page = doc.metadata["page_label"]  # the printed page number of this chunk
        if page not in pages:  # only add a page the first time it appears
            pages.append(page)  # keeps the best chunk's page first
    
    return answer, pages  # the answer text plus the pages the chunks came from