## DATE: 18/10/2026
## DAY 2: Covered the part from getting the embeddings model to writing and testing the retrieval of both chunking strategies

# IMPLEMENTATION
1. Wrote the get_embeddings_model function to get the embeddings model that will embed the chunked documents. The function takes the model name as an argument and returns the corresponding embeddings model.
2. Wrote the vector_store file to create a vector store to store the chunked documents with their embeddings. The persist directory is enabled to store the vector store on disk for future use.
3. Wrote the ingest file to ingest the chunked documents into the vector store. The function takes the collection name and a callable function that returns the chunked documents as arguments. It checks if the collection already exists in the vector store, and if not, it calls the callable function to get the chunked documents and adds them to the vector store.
4. Tested the ingestion function by providing a question and checking if the relevant chunks are retrieved from the vector store with the score.
5. Wrote the retriever file to retrieve the relevant chunks from the vector store based on the question provided. Also wrote the show_results function to display the retrieved chunks with their scores and sources.
6. Tested the retriever function by providing a question and checking if the relevant chunks are retrieved from the vector store with the score and source.


# LEARNINGS

## 1. Semantic chunker: type and amount
- It measures how different each sentence is from the next. Each difference is a "gap".
- Big gap means topic change. The chunker cuts where the gap is above a threshold.
- `breakpoint_threshold_type` is the rule for picking the threshold. Options: `percentile`, `standard_deviation`, `interquartile`, `gradient`.
- `breakpoint_threshold_amount` is the number that goes into that rule. Its meaning changes with the type. If left out, the type's default is used (95, 3, 1.5, 95).
- `percentile` with 95 cuts at the top 5% of gaps on that page. With 80 it cuts at the top 20%. Lower amount means more cuts and smaller chunks.
- With `percentile`, the number of chunks is mostly set by how many sentences a page has. The embedding model decides where the cuts fall.
- `standard_deviation` and `interquartile` can produce zero cuts, which leaves a whole page as one chunk. `percentile` always cuts at least once.
- Too low an amount gives one-sentence fragments. Too high gives huge chunks. There is no maximum chunk size, so always check the longest chunk.
- Other args: `buffer_size` (neighbours embedded with each sentence), `min_chunk_size` (merge tiny chunks), `sentence_split_regex` (what counts as a sentence).
- Tune by changing the amount first (95, 90, 80) and reading the chunks.

## 2. Semantic chunker: problems seen in my PDF
- Sentences end only at `. ? !`. A numbered heading like "5. Groundwater" leaves a stray `5.` at the end of the previous chunk.
- Page text ending in a newline gives an empty last chunk. Fix: keep only chunks where `c.strip()` is not empty. The recursive splitter already drops blanks, so it doesn't need this.
- A cut can leave a dangling reference, like a chunk starting "Its approval is needed...".
- Running header and footer stay inside chunks. Left in on purpose, to be cleaned in Project 2.

## 3. kwargs
- kwargs means keyword arguments, named settings like `chunk_size=1000`.
- `model_kwargs` applies when the model is loaded, for example `{"device": "cpu"}`.
- `encode_kwargs` applies each time text is turned into a vector, for example `{"normalize_embeddings": True}`.
- The wrapper passes these dictionaries straight to the library underneath, so the keys must match that library's names.

## 4. embeddings.py
- `get_embedding_model(model_name="BAAI/bge-m3")` returns a `HuggingFaceEmbeddings`.
- bge-m3 gives 1024-number vectors. The first run downloads about 2 GB. After that it is cached on the Mac.
- `normalize_embeddings=True` scales vectors to length 1, which suits BGE models.
- A different model has a different vector size, so it needs its own Chroma collection.
- Type hint: `Embeddings` (from `langchain_core.embeddings`) avoids Pylance "unknown type" warnings.
- Pylance wants `Literal[...]` for the threshold type, not `str`.

## 5. Chroma collections
- A collection is a named container inside the persist folder. One folder can hold many.
- `collection_name` decides which one you are writing to or reading from. Same name for two strategies would mix their chunks.
- One function is enough: `get_vector_store(embedding_model, collection_name)`. Call it once per chunk strategy with different names.
- Put the model and the setting in the name (`..._p80_bge_m3`), because a changed setting would otherwise be skipped by the guard.
- `is_empty(store)` is `not store.get(limit=1)["ids"]`. `get` fetches by position with no search. `limit=1` because we only need to know if anything exists. An empty list is false, so `not []` is true.
- Add the persist folder to `.gitignore`.

## 6. Callable, make_chunks, lambda
- A function is a value. `f` is the function, `f()` runs it.
- `Callable[[inputs], output]` is the type hint for a function parameter. `Callable[[], list[Document]]` means takes nothing, returns a list of Documents.
- `ingest(name, make_chunks)` receives the function unrun. It checks `is_empty` first and calls `make_chunks()` only if the store is empty.
- Passing the result directly would run the slow splitting before the check, on every run.
- `lambda: split_documents_recursive(docs)` wraps the function and its inputs into one function that needs no inputs.
- Name or `lambda:` means run later. Parentheses with arguments means run now.

## 7. List comprehension
- `chunks = [c for c in pieces if c.strip()]` means: go through the pieces, keep each one that has real text.
- `strip()` removes blank space from both ends. A blank chunk becomes `""`, which counts as false.
- Same as a for loop with an `if` and `append`.

## 8. Ingest flow
1. Load PDF into page Documents.
2. Open the collection by name.
3. If it has data, skip.
4. Otherwise split, then `add_documents` (embeds and stores).
- The semantic store embeds twice: once inside the chunker to find the gaps, once when storing the finished chunks.
- Result: recursive 23 chunks, semantic 39 chunks (percentile 80).

## 9. Reading retrieval output
- Line format: score, page_label, chunk text.
- Score is the distance. Lower means closer. It is a ranking number, not a percentage.
- Scores from two different stores can't be compared. The chunks differ.
- `similarity_search_with_score` returns the top `k` (default 4) whether they are good or not.
- Print the full chunk (`doc.page_content`), not a preview. The preview can hide the answer.
- Judge in this order: right page near the top, answer text inside the top chunk, what the noise is.
- A big jump in score after #1 (0.7 to 1.1) suggests one clear winner and filler after it. Only a hint from two questions. Test with an unanswerable question.
- Overlap can fill two result slots with the same sentences.

## 10. Findings so far (2 questions)
- Both stores put the right page first on both questions.
- Recursive chunks are bigger, with leftover text from neighbouring sections and mid-sentence starts.
- Semantic chunks are tighter, but can split one answer across two chunks.
- Traps: the budget chunk says Rs 5.6 crore for rainwater subsidies, which could be mistaken for the household subsidy.
- Not enough to pick a winner. Need the full question set.

