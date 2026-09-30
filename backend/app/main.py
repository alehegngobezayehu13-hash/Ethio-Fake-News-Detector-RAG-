from fastapi import FastAPI

app = FastAPI(
    title="Ethio Fake News Detector",
    description="RAG-based fake news checker for Amharic, English, Tigrinya and Afaan Oromo.",
    version="0.1.0",
)


@app.get("/health")
def health():
    """Simple endpoint to confirm the server is running."""
    return {"status": "ok"}