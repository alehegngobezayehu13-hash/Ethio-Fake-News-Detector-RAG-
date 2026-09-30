# Ethio Fake News Detector (RAG)

A web app that checks news claims written in Amharic, English, Tigrinya and Afaan Oromo
using Retrieval-Augmented Generation (RAG).

## How it works

1. Input: a user submits a news claim in any supported language.
2. Retrieve: the claim is embedded with a multilingual model and compared against a
   knowledge base of trusted sources and fact-checks.
3. Generate: an LLM reads the claim plus the retrieved evidence and returns a verdict
   (supported / contradicted / not enough evidence) with an explanation.

## Planned stack

- Backend: Python, FastAPI
- Embeddings: multilingual sentence-transformers model
- Vector search: FAISS
- LLM: to be decided
- Frontend: HTML, CSS, JavaScript

## Project structure

```
backend/app/     API and RAG logic
data/raw/        original collected documents
data/processed/  cleaned data and indexes (not committed)
frontend/        website
tests/           automated tests
docs/            notes and design decisions
```

## Status

Work in progress.
