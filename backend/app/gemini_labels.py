import argparse
import csv
import json      
import os
import random
import time
from collections import Counter, defaultdict

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from backend.app.chunker import DATA_DIR, OUTPUT_PATH as CHUNKS_PATH

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
OUT_DIR = DATA_DIR / "training"
OUT_PATH = OUT_DIR / "gemini_examples.jsonl"
DONE_PATH = OUT_DIR / "gemini_done.txt"
AUDIT_PATH = OUT_DIR / "gemini_audit.csv"

PASSAGES_PER_REQUEST = 5      
TRUE_PER_PASSAGE = 4   
FALSE_PER_PASSAGE = 4
UNSETTLED_PER_PASSAGE = 3
SECONDS_BETWEEN_CALLS = 6.0   
REQUEST_TIMEOUT_MS = 180_000  
MAX_ATTEMPTS = 4
MIN_CHUNK_CHARS = 150
SEED = 7

LANGUAGE_NAMES = {"am": "Amharic", "ti": "Tigrinya", "om": "Afaan Oromo", "en": "English"}
LABEL_MAP = {"TRUE": "supported", "FALSE": "contradicted", "UNSETTLED": "not_enough_evidence"}

PROMPT = """You are helping build a fact-checking dataset.

Below are {n} numbered PASSAGES from real news articles, all written in {language}.
For EACH passage, write exactly {true} TRUE, {false} FALSE and {unsettled} UNSETTLED claims about that passage. Write every claim in {language}, in the same script as the passages.

- TRUE: the passage clearly confirms the claim. Say it in different words. Do not copy a sentence from the passage.
- FALSE: the passage clearly contradicts the claim. Take a fact from the passage (a name, place, date, amount, who did what, or a negation) and change it.
- UNSETTLED: the claim is about the same story and sounds plausible, but the passage neither confirms nor contradicts it.

Rules: each claim is ONE sentence of 8 to 30 words and must stand on its own (never say "the passage" or "the article"). Judge each claim only against its own passage, never against another one. Use only what the passage says. A FALSE claim must be clearly wrong according to its passage. Do not repeat the same claim in different words.

Reply with JSON only, in this shape:
{{"passages": [{{"id": 1, "claims": [{{"text": "...", "label": "TRUE"}}, {{"text": "...", "label": "FALSE"}}, {{"text": "...", "label": "UNSETTLED"}}]}}, {{"id": 2, "claims": []}}]}}

{passages}
"""


def article_id(chunk: dict) -> str:
    return chunk["id"].rsplit("-", 1)[0]


def split_for(article: str) -> str:
    """Same rule as the example builder: whole articles go to one split."""
    bucket = int(article, 16) % 10
    return "test" if bucket == 0 else "val" if bucket == 1 else "train"


def make_batches(chunks: list[dict], done: set[str], size: int) -> list[list[dict]]:
    """Groups of passages in one language. The four languages take turns, so
    Tigrinya and Afaan Oromo are not crowded out by Amharic."""
    rng = random.Random(SEED)
    groups = defaultdict(list)
    for chunk in chunks:
        if len(chunk["text"]) >= MIN_CHUNK_CHARS and chunk["id"] not in done:
            groups[chunk["language"]].append(chunk)
    for group in groups.values():
        rng.shuffle(group)

    batches: list[list[dict]] = []
    while any(groups[language] for language in LANGUAGE_NAMES):
        for language in LANGUAGE_NAMES:
            group = groups[language]
            if group:
                batches.append([group.pop() for _ in range(min(size, len(group)))])
    return batches


def build_prompt(batch: list[dict]) -> str:
    passages = "\n\n".join(f"=== PASSAGE {i} ===\n{chunk['text']}" for i, chunk in enumerate(batch, start=1))
    return PROMPT.format(
        n=len(batch),
        language=LANGUAGE_NAMES[batch[0]["language"]],
        true=TRUE_PER_PASSAGE,
        false=FALSE_PER_PASSAGE,
        unsettled=UNSETTLED_PER_PASSAGE,
        passages=passages,
    )


def clean_claims(items: list, passage: str) -> list[dict]:
    """Keep only claims that look usable."""
    claims, seen = [], set()
    for item in items:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        label = LABEL_MAP.get(str(item.get("label", "")).strip().upper())
        if not label or not 15 <= len(text) <= 300:
            continue
        if text in passage or text in seen:
            continue  
        seen.add(text)
        claims.append({"claim": text, "label": label})
    return claims


def parse_batch(raw: str, batch: list[dict]) -> dict[int, list[dict]] | None:
    """Read Gemini's reply. Returns {passage number: claims}, or None if it can't be read."""
    try:
        data = json.loads(raw.strip().removeprefix("```json").removesuffix("```"))
        items = data["passages"]
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return None
    if not isinstance(items, list):
        return None

    result: dict[int, list[dict]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("claims"), list):
            continue
        try:
            number = int(item.get("id"))
        except (TypeError, ValueError):
            continue
        if 1 <= number <= len(batch):
            result[number] = clean_claims(item["claims"], batch[number - 1]["text"])
    return result or None


def generate(client, prompt: str, model: str) -> str:
    """One Gemini call, retrying when Google is busy or the minute limit is hit."""
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.6, response_mime_type="application/json"),
            )
            return response.text or ""
        except errors.APIError as e:
            if e.code not in (429, 503) or attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(10 * 2**attempt)  
    return ""


def make_record(claim: dict, chunk: dict, model: str) -> dict:
    article = article_id(chunk)
    return {
        "claim": claim["claim"],
        "evidence": chunk["text"],
        "label": claim["label"],
        "language": chunk["language"],
        "kind": "gemini",
        "article": article,
        "evidence_article": article,
        "split": split_for(article),
        "chunk_id": chunk["id"],
        "model": model,
    }


def write_audit(path=AUDIT_PATH, source=OUT_PATH) -> None:
    """100 Gemini examples for you to check by hand, to measure how often it is wrong."""
    if path.exists() or not source.exists():
        return
    with open(source, encoding="utf-8") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    by_language = defaultdict(list)
    for row in rows:
        by_language[row["language"]].append(row)
    if sum(len(v) for v in by_language.values()) < 100:
        return
    rng = random.Random(SEED)
    sample = []
    for language in sorted(by_language):
        items = by_language[language]
        sample.extend(rng.sample(items, min(25, len(items))))
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "language", "claim", "evidence", "gemini_label", "your_check"])
        writer.writeheader()
        for n, row in enumerate(sample, start=1):
            writer.writerow({"id": n, "language": row["language"], "claim": row["claim"],
                             "evidence": row["evidence"], "gemini_label": row["label"], "your_check": ""})
    print(f"Wrote {AUDIT_PATH.name}: type ok or wrong in the your_check column to measure Gemini's accuracy.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Label claims with Gemini.")
    parser.add_argument("--max-calls", type=int, default=100, help="requests to make in this run")
    parser.add_argument("--passages", type=int, default=PASSAGES_PER_REQUEST, help="passages per request")
    parser.add_argument("--model", default=MODEL, help="Gemini model ID, copied from Google AI Studio")
    args = parser.parse_args()

    if not CHUNKS_PATH.exists():
        print("No chunks found. Run the chunker first.")
        return
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f if line.strip()]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    done = set(DONE_PATH.read_text(encoding="utf-8").split()) if DONE_PATH.exists() else set()
    batches = make_batches(chunks, done, args.passages)
    print(f"Model: {args.model}")
    print(f"{len(done)} passages already done, {sum(len(b) for b in batches)} left in {len(batches)} requests.")
    print(f"This run makes up to {args.max_calls} requests of {args.passages} passages each.")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS))
    calls = made = 0
    for batch in batches[: args.max_calls]:
        try:
            raw = generate(client, build_prompt(batch), args.model)
        except errors.APIError as error:
            print(f"Stopping: Gemini refused the request ({error.code}). The daily limit of this model may be used up.")
            print("Run again later, or use another free model with --model.")
            break
        except Exception as error:  
            print(f"  request failed ({type(error).__name__}), skipping this group")
            continue

        parsed = parse_batch(raw, batch)
        if not parsed:
            print("  could not read the reply, skipping this group. If this keeps happening, use --passages 3")
            continue
        with open(OUT_PATH, "a", encoding="utf-8") as f:
            for number, claims in parsed.items():
                for claim in claims:
                    f.write(json.dumps(make_record(claim, batch[number - 1], args.model), ensure_ascii=False) + "\n")
        with open(DONE_PATH, "a", encoding="utf-8") as f:
            for number in parsed:
                f.write(batch[number - 1]["id"] + "\n")
        calls += 1
        made += sum(len(claims) for claims in parsed.values())
        if calls % 10 == 0:
            print(f"  {calls} requests made, {made} examples so far in this run")
        time.sleep(SECONDS_BETWEEN_CALLS)

    print(f"\nThis run: {calls} requests, {made} examples.")
    if OUT_PATH.exists():
        with open(OUT_PATH, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        print(f"Total Gemini examples so far: {len(rows)}")
        print("By label:   ", dict(Counter(r["label"] for r in rows)))
        print("By language:", dict(Counter(r["language"] for r in rows)))
        print("By model:   ", dict(Counter(r.get("model", "earlier run") for r in rows)))
        write_audit()


if __name__ == "__main__":
    main()