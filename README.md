# Ethio Fake News Detector (RAG)

A multilingual web application for checking news claims in **Amharic, English, Tigrinya, and Afaan Oromo** using Retrieval-Augmented Generation (RAG).

The system retrieves relevant evidence from a collected knowledge base and evaluates the claim with a locally integrated fine-tuned multilingual verdict model. It returns one of three assessments:

- `supported`
- `contradicted`
- `not_enough_evidence`

The system is designed to help users inspect evidence behind a claim. A model assessment is not an independently verified fact.

## Features

- Multilingual claim checking
- Support for Amharic, English, Tigrinya, and Afaan Oromo
- Multilingual semantic embeddings
- FAISS-based evidence retrieval
- Fine-tuned multilingual verdict classifier
- Evidence and available source metadata in results
- Browser-based frontend
- FastAPI backend
- Automatic FastAPI API documentation
- Cached retrieval index for reuse between runs

## How It Works

1. **Input** — A user submits a news claim through the website.
2. **Embedding** — The claim is converted into a multilingual vector representation.
3. **Retrieval** — FAISS searches the knowledge base for relevant evidence.
4. **Verdict** — The trained verdict model evaluates the claim against the retrieved evidence.
5. **Result** — The website displays the verdict, explanation, evidence, and available source information.

## Technology Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Embeddings:** Sentence Transformers multilingual model
- **Vector Search:** FAISS
- **Verdict Model:** Fine-tuned multilingual transformer classifier
- **Frontend:** HTML, CSS, JavaScript
- **Data:** JSONL and processed vector/index files

## Supported Languages

The system supports:

- Amharic
- English
- Tigrinya
- Afaan Oromo

## Verdicts

The system provides three possible assessments:

### `supported`

The available retrieved evidence supports the submitted claim.

### `contradicted`

The available retrieved evidence contradicts the submitted claim.

### `not_enough_evidence`

The available evidence is insufficient to confidently support or contradict the claim.

The verdict is a **model assessment based on the available evidence** and should not be treated as an independently verified fact.

## Project Structure

```text
Ethio-Fake-News-Detector-RAG/
├── backend/
│   └── app/
│       ├── main.py
│       ├── crawler.py
│       └── ...
├── data/
│   ├── crawled/
│   ├── training/
│   └── processed/
├── frontend/
├── tests/
├── docs/
├── notebooks/
├── README.md
├── LICENSE
└── ...
```

Large model files, processed indexes, and generated datasets may be excluded from Git when appropriate.

## Running the Project Locally

From the project root, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then start the FastAPI server:

```powershell
uvicorn backend.app.main:app --reload
```

After the server starts, open:

```text
http://127.0.0.1:8000/
```

The FastAPI interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### First Startup

The first startup may take longer, especially on a CPU-only machine, because the embedding model and retrieval index may need to load or be prepared.

Wait until the terminal displays:

```text
Application startup complete.
```

before sending requests.

Once the required models and retrieval index are ready, normal requests should be considerably faster.

## Evidence and Sources

The system uses collected news and fact-checking documents as evidence.

Where available, the system preserves source information such as:

- Source or publisher
- Article/document title
- Language
- Source URL

The availability of source metadata depends on the original collected document.

Users can inspect available source information to better understand the evidence behind a model assessment.

## Project Status

**Completed project implementation / final release.**

The main application workflow has been implemented:

- Claim submission
- Multilingual processing
- Evidence retrieval
- Verdict classification
- Explanation generation/presentation
- Evidence presentation
- Source metadata presentation
- Browser-based user interface
- FastAPI backend

The system is considered complete as a project implementation. However, its predictions can still be incorrect and should be evaluated carefully on new and unseen claims.

## Documentation

Additional project documentation is available in the `docs/` directory.

This includes the Software Requirements Specification (SRS) when it is included in the repository.

## License

This project is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for the complete license text.

Copyright (c) 2026 Alehegn Gobezayehu