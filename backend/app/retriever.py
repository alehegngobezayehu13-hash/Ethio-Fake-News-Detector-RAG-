import hashlib
from pathlib import Path

import faiss
import numpy as np

from backend.app.documents import DATA_DIR, Document, load_all_documents
from backend.app.embeddings import MODEL_NAME, embed_passages, embed_query

CACHE_DIR = DATA_DIR / "processed" / "index"


def passage_text(doc: Document) -> str:
    return f"{doc.title}\n{doc.text}" if doc.title else doc.text


def fingerprint(texts: list[str]) -> str:
    digest = hashlib.sha1(MODEL_NAME.encode("utf-8"))
    for text in texts:
        digest.update(text.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def load_or_embed(texts: list[str], cache_dir: Path) -> np.ndarray:
    vectors_path = cache_dir / "embeddings.npy"
    fingerprint_path = cache_dir / "fingerprint.txt"
    current = fingerprint(texts)
    if vectors_path.exists() and fingerprint_path.exists():
        if fingerprint_path.read_text() == current:
            return np.load(vectors_path)

    print(f"Embedding {len(texts)} passages (this only happens when the data changes)...")
    vectors = np.ascontiguousarray(embed_passages(texts), dtype="float32")
    cache_dir.mkdir(parents=True, exist_ok=True)
    np.save(vectors_path, vectors)
    fingerprint_path.write_text(current)
    return vectors


class Retriever:
    def __init__(self, documents: list[Document], cache_dir: Path = CACHE_DIR):
        self.documents = documents
        vectors = load_or_embed([passage_text(d) for d in documents], cache_dir)
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(self, claim: str, k: int = 3) -> list[tuple[Document, float]]:
        k = min(k, len(self.documents))
        query = np.ascontiguousarray(embed_query(claim), dtype="float32").reshape(1, -1)
        scores, ids = self.index.search(query, k)
        return [
            (self.documents[i], float(s))
            for i, s in zip(ids[0], scores[0])
            if i != -1
        ]


if __name__ == "__main__":
    retriever = Retriever(load_all_documents())
    for claim in ["መንግስት አዲስ የትምህርት ፖሊሲ አወጣ", "How many months are in the Ethiopian calendar?"]:
        print(f"\nClaim: {claim}")
        for doc, score in retriever.search(claim, k=3):
            print(f"  {score:.3f} [{doc.language}] {doc.source}: {doc.text[:80]}")