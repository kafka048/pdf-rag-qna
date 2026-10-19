## DATE: 19/10/2026
## DAY 3: Covered the generator, the pipeline function, the evaluation of both chunking strategies on my own question set, and the FastAPI endpoint. Project 1 built end to end.

# IMPLEMENTATION
1. Wrote the generator file. `format_context` labels each retrieved chunk with its page and joins them, `PROMPT_TEMPLATE` tells the model to answer only from the context and say "I could not find this in the document." if it is missing, `get_llm` connects to Ollama with temperature 0, and `generate_answer` fills the prompt and calls the model.
2. Wrote the pipeline file. `answer_question(store, llm, question, k)` retrieves, generates, and returns the answer plus the de-duplicated pages of the retrieved chunks.
3. Pulled qwen3:8b alongside llama3.1:8b. Tested generation first with llama3.1:8b on one question against both stores.
4. Wrote the questions file: 10 questions with expected answer, page and what each one tests (one is unanswerable), plus a `FACTS` dict of the key facts per question.
5. Added the retrieval evaluation to test.py: first a page-level check, then a stricter check that all key facts sit in one chunk.
6. Debugged the one semantic miss (Q8) by printing the chunk that holds "31 percent".
7. Wrote run_answers.py to send all questions through the model and print the answers next to the expected facts. Ran the recursive store with qwen3:8b. Stopped the semantic run because the Mac was lagging.
8. Wrote api.py, a FastAPI app with `POST /ask`. Tested it in Postman.
9. Wrote the README (what we did, how to run, limitations).

# LEARNINGS

## 1. Generation
- The prompt does the work. Answer only from the context, say a fixed sentence if it is missing, cite pages.
- Temperature 0 so the same question gives the same answer.
- `"\n\n".join(...)` turns a list of strings into one string with blank lines between them.
- `for doc, _score in results` unpacks each (Document, score) pair. `_score` marks a value I do not use. A plain name `score` would work too, it is only a convention.

## 2. Models
- llama3.1:8b answers directly. qwen3:8b reasons before answering, so it is slower and heats the Mac more.
- qwen3:8b can print its thinking text. In my runs the answers came out clean.
- Mistral 7B is open source (Apache 2.0) but older.
- A 14B model is tight on 16 GB RAM next to bge-m3.
- Run one model at a time. `ollama ps` shows what is loaded, `ollama stop <model>` unloads it.

## 3. How to evaluate retrieval
- Retrieve once, keep the same chunks, change one thing at a time.
- Page-level check is weak here. The PDF has 8 pages and k is 4, so half the document comes back.
- Strict check is better. All key facts must sit in the same normalized chunk. Also look at the rank, not only whether it is in the top 4.
- Separate retrieval failure from generation failure. Check the retrieved chunks first.

## 4. Retrieval results
- Page-level: 9 of 9 for both stores at rank 1.
- Strict: recursive 9 of 9 in the top 4 and 7 of 9 at rank 1. Semantic 8 of 9 in the top 4 and 6 of 9 at rank 1.
- Q2 semantic: the BPL rate sits in its own small chunk, so it ranked 2nd.
- Q4 both stores: the answer is spread over several chunks, so rank 3.
- Q8 semantic miss: the chunk with "31 percent" starts "It combined trained volunteers..." and never names Karanpur. The cut fell between two sentences that both start with "It".
- Lesson: a chunk that needs its neighbour to make sense will fail even when the right page is found.

## 5. Scores and abstaining
- Scores are distances. Lower is closer. They are not comparable across stores.
- There is no universal cutoff. The unanswerable Q10 had a top score of 0.969, lower than some answerable questions.
- So abstaining relies on the prompt, not a score threshold.

## 6. Scoring the answers
- Three outcomes: correct, grounded (supported by the chunks but not the expected fact), abstained.
- Recursive store with qwen3:8b: all 10 fine. Q10 correctly abstained.
- Q4 was incomplete. It missed the daily rain gauge reading and added extra details (honorarium, neighbouring villages). Check extras against the PDF before calling them grounded.
- Semantic store was not run through the model.

## 7. FastAPI endpoint
- Load the embedding model, store and LLM once at the top of api.py, so the server pays that cost at startup and not per request.
- Two Pydantic classes declare the JSON shape: `AskRequest` (question) and `AskResponse` (answer, sources).
- `@app.post("/ask")` registers the function. A plain `def` is right because the model call blocks, and FastAPI runs it on a separate thread.
- Run from the project root: `uvicorn api:app --app-dir src --port 8001`. `--app-dir src` makes `api` importable while the working folder stays the root.
- `/docs` gives a built-in test page. Postman needs POST, Body, raw, JSON.
- Port 8000 was already in use, so I used 8001. `lsof -i :8000` shows what holds a port.

## 8. Gotchas
- The persist path `chroma_persist_db` is relative to the folder the program starts in. Starting from the wrong folder silently creates a new, empty store.
- An empty store returned `sources: []` and the model still invented a wrong answer ("first Tuesday", page 4). The prompt alone does not stop a model from guessing when there is no context at all. Worth guarding in code later: no retrieved chunks means return "not found" without calling the model.
- A fresh clone needs the stores built before the API returns anything. The README has to say so.
- Disk: Ollama models use about 10 GB. The Hugging Face cache holds other projects' models, do not delete it. Part of the unexplained disk drop is likely a staged macOS update (not confirmed).

## 9. Known limitations
- The page header and footer sit in every chunk. To be cleaned in Project 2.
- Chunks cannot cross a page boundary.
- No score cutoff for abstaining.
- Tested on one PDF and 10 questions.

