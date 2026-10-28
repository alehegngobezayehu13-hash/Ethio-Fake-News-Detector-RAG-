from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.app.documents import load_all_documents
from backend.app.retriever import Retriever
from backend.app.verdict import check_claim


TOP_K = 5

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.retriever = Retriever(load_all_documents())
    yield


app = FastAPI(
    title="Ethio Fake News Detector",
    description=(
        "RAG-based fake news checker for Amharic, English, "
        "Tigrinya and Afaan Oromo."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


class CheckRequest(BaseModel):
    claim: str = Field(max_length=1000)


class EvidenceItem(BaseModel):
    language: str
    text: str
    source: str
    url: str
    title: str


class CheckResponse(BaseModel):
    claim: str
    verdict: str
    explanation: str
    evidence: list[EvidenceItem]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check", response_model=CheckResponse)
def check(body: CheckRequest, request: Request):
    claim = body.claim.strip()

    if len(claim) < 3:
        raise HTTPException(
            status_code=400,
            detail="Claim is too short.",
        )

    # Retrieve relevant evidence from the knowledge base.
    results = request.app.state.retriever.search(
        claim,
        k=TOP_K,
    )

    evidence_docs = [
        doc
        for doc, _ in results
    ]

    # Use the trained verdict model.
    verdict = check_claim(
        claim,
        evidence_docs,
    )

    return CheckResponse(
        claim=claim,
        verdict=verdict["verdict"],
        explanation=verdict["explanation"],
        evidence=[
            EvidenceItem(
                language=doc.language,
                text=doc.text,
                source=doc.source,
                url=doc.url,
                title=doc.title,
            )
            for doc, _ in results
        ],
    )


app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_DIR,
        html=True,
    ),
    name="frontend",
)