import json
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "knowledge_base.json"
SUPPORTED_LANGUAGES = {"en", "am", "ti", "om"}

@dataclass
class Document:
    id: str
    language: str
    topic: str
    text: str
    source: str

def load_documents(path: Path = DEFAULT_PATH) -> list[Document]:
    """Read the JSON file and return a list of validated Document objects."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    documents = []
    for item in raw:
        if item["language"] not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language in {item['id']}: {item['language']}")
        if not item["text"].strip():
            raise ValueError(f"Empty text in {item['id']}")
        documents.append(Document(**item))
    return documents

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    for d in docs[:4]:
        print(d.id, "|", d.text)