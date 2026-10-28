from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from backend.app.documents import Document


MODEL_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "models"
    / "verdict-model"
)

MAX_LEN = 256

LABELS = [
    "supported",
    "contradicted",
    "not_enough_evidence",
]

ID2LABEL = {
    0: "supported",
    1: "contradicted",
    2: "not_enough_evidence",
}


print(f"Loading verdict model from: {MODEL_DIR}")

if not MODEL_DIR.exists():
    raise FileNotFoundError(
        f"Verdict model directory was not found: {MODEL_DIR}"
    )


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_DIR,
    num_labels=len(LABELS),
)

model.to(DEVICE)
model.eval()

print("Verdict model loaded successfully.")


def predict_pair(claim: str, evidence_text: str) -> int:
    

    inputs = tokenizer(
        claim,
        evidence_text,
        truncation="only_second",
        max_length=MAX_LEN,
        padding=True,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        outputs = model(**inputs)

    predicted_id = int(
        torch.argmax(outputs.logits, dim=-1).item()
    )

    return predicted_id


def check_claim(claim: str, evidence: list[Document]) -> dict:

    if not evidence:
        return {
            "verdict": None,
            "explanation": (
                "No evidence was retrieved for this claim."
            ),
            "evidence": [],
        }

    predictions = []

    for doc in evidence:
        predicted_id = predict_pair(
            claim,
            doc.text,
        )

        predictions.append(predicted_id)

    counts = {
        label_id: predictions.count(label_id)
        for label_id in range(len(LABELS))
    }

    final_id = max(
        counts,
        key=counts.get,
    )

    final_verdict = ID2LABEL[final_id]

    if final_verdict == "supported":
        explanation = (
            "The retrieved evidence supports the claim."
        )

    elif final_verdict == "contradicted":
        explanation = (
            "The retrieved evidence contradicts the claim."
        )

    else:
        explanation = (
            "The retrieved evidence does not provide "
            "enough relevant information to support or "
            "contradict the claim."
        )

    return {
        "verdict": final_verdict,
        "explanation": explanation,
        "evidence": evidence,
    }