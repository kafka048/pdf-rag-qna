# pdf-rag-qna

Ask questions about a PDF and get answers grounded in it, with page numbers. Runs fully locally with no API keys.

## What we did

- Loaded the PDF page by page, split it into chunks, embedded them with bge-m3 and stored them in Chroma.
- Built two stores to compare chunking: recursive (23 chunks) and semantic (39 chunks).
- Retrieved the top 4 chunks for a question and answered from them only, using qwen3:8b through Ollama.
- If the answer isn't in the chunks, the model says "I could not find this in the document."
- Wrapped it in a FastAPI endpoint, `POST /ask`, which returns the answer and the source pages.
- Tested on a fictional 8 page water handbook with 10 questions. The recursive store with qwen3:8b answered all 10 correctly, including one unanswerable question. Recursive also retrieved better than semantic.

## How to run

Install the packages and pull the model:

```
pip install -r requirements.txt
ollama pull qwen3:8b
```

Start the API from the project root:

```
uvicorn api:app --app-dir src --port 8001
```

Ask a question:

```
curl -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" -d '{"question": "When is the Jal Chaupal held each month?"}'
```

## Limitations

- The page header and footer are part of each page's text and add noise to retrieval.
- Chunks can't cross a page boundary, so a paragraph that runs onto the next page is always cut.
- Semantic chunking can drop context: one chunk lost the word "Karanpur" because of a cut between two sentences that both start with "It".
- There is no score cutoff for abstaining, so it relies on the prompt alone.
- The semantic store wasn't run through the model, only tested on retrieval.
- Tested on one document and 10 questions.