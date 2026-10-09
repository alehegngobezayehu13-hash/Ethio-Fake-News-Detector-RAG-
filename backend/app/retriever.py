import faiss
import numpy as np

from backend.app.documents import Document, load_documents
from backend.app.embeddings import embed_passages, embed_query

class Retriever:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        vectors = np.ascontiguousarray(
            embed_passages([d.text for d in documents]), dtype="float32"
        )
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
    retriever = Retriever(load_documents())
    for claim in ["መንግስት አዲስ የትምህርት ፖሊሲ አወጣ", "How many months are in the Ethiopian calendar?"]:
        print(f"\nClaim: {claim}")
        for doc, score in retriever.search(claim, k=3):
            print(f"  {score:.3f} [{doc.language}] {doc.text}")