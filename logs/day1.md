## DATE: 17/10/2026
## Day 1: PDF Text Extraction and Chunking

1. Used the PyPDFLoader library to extract text from the pdf document. 
2. Tested the document loading and text extraction process to ensure that the text is correctly retrieved from the PDF.
3. Wrote the splitter and the two functions for chunking recursively, and semantically after installing a new langchain_experimental package.

# LEARNINGS

## 1. Reading the loaded PDF
- `documents[n].page_content` is the correct way to access the text content of the document in the list of documents returned by the PDF loader, where n is the index of the document in the list. It is 0-indexed, so the first document is `documents[0].page_content`, the second is `documents[1].page_content`, and so on.
- `documents[n].metadata` prints all the relevant metadata for the document, including the page number, source, page label, and any other metadata that was extracted from the PDF. This can be useful for debugging and understanding the structure of the document.

## 2. PDF loading gotchas

### Running header and footer are inside the page text
- `PyPDFLoader` returns the whole page, including the header ("Nandpur District Water Security Handbook, 2026 Edition / District Water Office, Nandpur") and the "Page N" footer. They sit at the top of `page_content` for every page.
- Effect: the first chunk of every page carries the same three lines, which pulls those chunks toward the same vector and adds noise to retrieval.
- Plan: keep it as is for the baseline, because real PDFs look like this. Later, strip the header and footer as a separate experiment and compare retrieval on the same question set. This will be cleaned in Project 2 and it is retained so that we can understand how this noise hurts retrieval and answer generation.

### Chunks cannot cross a page boundary
- The loader gives one `Document` per page, and the splitter runs on each page separately.
- Effect: a paragraph that continues onto the next page is cut at the page break, and overlap cannot fix it, because the overlap only works inside one page's text.
- Example: the Jal Chaupal paragraph (section 3.5) starts on page 3 and finishes on page 4, so it is always split into two chunks.
- Tradeoff: this is the price of having a reliable page number on every chunk.
- Watch for: a retrieval miss where the answer sits near the top or bottom of a page.
- Possible later fix: join all pages into one text, split it, then map each chunk back to its page.

### Page metadata
- `page` is 0-indexed (the second page shows `page: 1`).
- `page_label` is the printed page number as a string (`'2'`), and it comes from the PDF itself.
- Decide which one the answers should cite. For user experience, `page_label` is better.

## 3. SemanticChunker

**How it works:** split into sentences, embed each (with neighbours), measure the distance between neighbours, cut where the distance is above a threshold.

### Args
- `embeddings` (required): the model that judges meaning. Use your local one.
- `buffer_size` (1): neighbour sentences glued to each sentence before embedding. Higher means smoother, fewer cuts.
- `breakpoint_threshold_type` ("percentile"): the rule for picking the threshold.
- `breakpoint_threshold_amount` (None, uses the type's default): the number for that rule. Higher means fewer, bigger chunks.
- `number_of_chunks` (None): target chunk count. Overrides type and amount. Approximate.
- `sentence_split_regex` (split after `. ? !`): how sentences are found. Text without punctuation never splits.
- `min_chunk_size` (None): chunks shorter than this many characters merge into the next one.
- `add_start_index` (False): adds start position to metadata. No effect with `split_text`.

### Threshold types (default amount)
- `percentile` (95): cut at the top 5% of jumps.
- `standard_deviation` (3): mean + 3 x std.
- `interquartile` (1.5): mean + 1.5 x IQR.
- `gradient` (95): percentile of the rate of change. For text where topics blend.

Do not reuse an amount across types.

### Remember
- No max chunk size. A chunk can be any length, so check the longest.
- A one-sentence page returns as one chunk, no crash.
- The threshold is per page, since you pass one page at a time.
- The page 7 table has no punctuation, so it will glue together. Try a regex that also splits on newlines.
- The package is deprecated but works.

### Tune order
Defaults, then `breakpoint_threshold_amount` (80, 90, 95), then `buffer_size` and `min_chunk_size`. One change at a time.