# Project 1: Single-Document RAG Q&A

Part of my 10-project RAG learning ladder. This is the first rung: the plain mechanics, end to end, on one PDF.

**Status:** in progress

## What it does

Ask natural-language questions about a single PDF and get an answer grounded in that document, with the page it came from. If the PDF does not contain the answer, it says so instead of guessing. Everything runs locally, with no API keys.

## Pipeline

Load PDF, split into chunks, embed, store in Chroma, retrieve the top-k chunks for a question, generate an answer with a local LLM.

## Scope

In scope:

- One PDF at a time
- Page numbers kept as sources
- Persistent vector store, so a restart does not re-embed
- One FastAPI endpoint: `POST /ask`

## Learnings:
