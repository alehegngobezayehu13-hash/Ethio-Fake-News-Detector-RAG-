from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from google.genai import errors as genai_errors
from pydantic import BaseModel, Field

from backend.app.documents import load_documents
from backend.app.retriever import Retriever
from backend.app.verdict import check_claim

TOP_K = 3


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build the search index once at startup, not on every request.
    app.state.retriever = Retriever(load_documents())
    yield


app = FastAPI(
    title="Ethio Fake News Detector",
    description="RAG-based fake news checker for Amharic, English, Tigrinya and Afaan Oromo.",
    version="0.1.0",
    lifespan=lifespan,
)


class CheckRequest(BaseModel):
    claim: str = Field(max_length=1000)


class EvidenceItem(BaseModel):
    id: str
    language: str
    text: str
    source: str
    score: float


class CheckResponse(BaseModel):
    claim: str
    verdict: str
    explanation: str
    evidence_ids: list[str]
    evidence: list[EvidenceItem]


@app.get("/health")
def health():
    """Simple endpoint to confirm the server is running."""
    return {"status": "ok"}


@app.post("/check", response_model=CheckResponse)
def check(body: CheckRequest, request: Request):
    """Check a claim: retrieve evidence, then ask the LLM for a verdict."""
    claim = body.claim.strip()
    if len(claim) < 3:
        raise HTTPException(status_code=400, detail="Claim is too short.")

    results = request.app.state.retriever.search(claim, k=TOP_K)
    evidence_docs = [doc for doc, _ in results]

    try:
        verdict = check_claim(claim, evidence_docs)
    except genai_errors.APIError:
        raise HTTPException(
            status_code=502,
            detail="The language model is unavailable right now. Please try again.",
        )

    return CheckResponse(
        claim=claim,
        verdict=verdict["verdict"],
        explanation=verdict["explanation"],
        evidence_ids=verdict["evidence_ids"],
        evidence=[
            EvidenceItem(
                id=doc.id,
                language=doc.language,
                text=doc.text,
                source=doc.source,
                score=score,
            )
            for doc, score in results
        ],
    )