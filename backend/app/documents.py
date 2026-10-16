import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DEFAULT_PATH = DATA_DIR / "raw" / "knowledge_base.json" 
CHUNKS_PATH = DATA_DIR / "processed" / "chunks.jsonl"   
SUPPORTED_LANGUAGES = {"en", "am", "ti", "om"}


@dataclass
class Document:
    id: str
    language: str
    text: str
    source: str
    topic: str = ""
    url: str = ""
    title: str = ""


def check(item: dict) -> Document:
    document = Document(**item)
    if document.language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language in {document.id}: {document.language}")
    if not document.text.strip():
        raise ValueError(f"Empty text in {document.id}")
    return document


def load_documents(path: Path = DEFAULT_PATH) -> list[Document]:
    with open(path, encoding="utf-8") as f:
        return [check(item) for item in json.load(f)]


def load_chunks(path: Path = CHUNKS_PATH) -> list[Document]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [check(json.loads(line)) for line in f if line.strip()]


def load_all_documents() -> list[Document]:
    return load_chunks() or load_documents()


if __name__ == "__main__":
    docs = load_all_documents()
    print(f"Loaded {len(docs)} documents")
    for d in docs[:4]:
        print(d.id, "|", d.source, "|", d.text[:80])