from langchain_core.documents import Document
from langchain_ollama import OllamaLLM

def format_context(results: list[tuple[Document, float]]) -> str:  # takes (chunk, score) pairs, returns one text block
    blocks: list[str] = [] # will hold one formatted string per chunk
    for doc, _score in results: # go through each pair; _score is unused, so it gets a throwaway name. 
        # a leading underscore tells them that this variable is being received but not used
        page_number = doc.metadata["page_label"]
        blocks.append(f"[Page {page_number}]\n{doc.page_content}")
    
    return "\n\n".join(blocks) # join takes a list of strings and returns one single string. It puts the text you call it on, here "\n\n", between the items.

PROMPT_TEMPLATE: str = """ You answer questions using only the context below.
If the context does not contain the answer, say: I could not find this in the document.
Cite the page numbers you used, like (page 4).

Context:
{context}

Question: {question}

Answer:
"""


def get_llm(model_name: str = "llama3.1:8b") -> OllamaLLM:
    return OllamaLLM(model=model_name, temperature=0) # temperature=0 means least random, so the same prompt gives (nearly) the same answer

def generate_answer(llm: OllamaLLM, question: str, results: list[tuple[Document, float]]) -> str:
    context = format_context(results)  # turn the chunks into one text block with [Page N] labels
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)  # fill {context} and {question} in the template
    return llm.invoke(prompt)  # send the prompt to Ollama and return its answer as a string
