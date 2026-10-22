import csv
import json
import random
import re
from collections import Counter, defaultdict

from backend.app.chunker import DATA_DIR, INPUT_PATH, build_chunks

OUT_DIR = DATA_DIR / "training"
EXAMPLES_PATH = OUT_DIR / "examples.jsonl"
LABEL_FILE = OUT_DIR / "to_label.csv"

SEED = 7
MIN_SENTENCE_CHARS = 40
SENTENCES_PER_ARTICLE = 3
HEADLINE_CHUNKS = 2
LABEL_ROWS_PER_LANGUAGE = 25

SENTENCE_SPLIT = re.compile(r"(?<=[.!?።፧])\s+")
NUMBER = re.compile(r"\d+")
WORD = re.compile(r"\w+")


def article_id(chunk: dict) -> str:
    return chunk["id"].rsplit("-", 1)[0]


def split_for(article: str) -> str:
    """Whole articles go to one split, so no article leaks across train and test."""
    bucket = int(article, 16) % 10
    return "test" if bucket == 0 else "val" if bucket == 1 else "train"


def headline(title: str) -> str:
    """Drop the site name that follows the last ' - ' in a page title."""
    return title.rsplit(" - ", 1)[0].strip() if " - " in title else title.strip()


def sentences(chunk: dict) -> list[str]:
    found = []
    for line in chunk["text"].split("\n"):
        for sentence in SENTENCE_SPLIT.split(line):
            sentence = sentence.strip()
            if len(sentence) >= MIN_SENTENCE_CHARS:
                found.append(sentence)
    return found


def change_number(sentence: str, rng: random.Random) -> str | None:
    """Replace one number with a different one, turning a true claim into a false one."""
    matches = list(NUMBER.finditer(sentence))
    if not matches:
        return None
    match = rng.choice(matches)
    old = int(match.group())
    new = old
    while new == old:
        new = max(0, old + rng.choice([-3, -2, -1, 1, 2, 3, 10]))
    return sentence[:match.start()] + str(new) + sentence[match.end():]


def make(claim: str, evidence: dict, label: str, source: dict, kind: str) -> dict:
    return {
        "claim": claim,
        "evidence": evidence["text"],
        "label": label,
        "language": source["language"],
        "kind": kind,
        "article": article_id(source),
        "evidence_article": article_id(evidence),
        "split": split_for(article_id(source)),
    }


def build_examples(chunks: list[dict], rng: random.Random) -> list[dict]:
    by_article = defaultdict(list)
    pool = defaultdict(list)  
    for chunk in chunks:
        by_article[article_id(chunk)].append(chunk)
        pool[(chunk["language"], split_for(article_id(chunk)))].append(chunk)

    def other_chunk(chunk: dict) -> dict | None:
        """A chunk from a different article, same language and split."""
        options = [
            c for c in pool[(chunk["language"], split_for(article_id(chunk)))]
            if article_id(c) != article_id(chunk)
        ]
        return rng.choice(options) if options else None

    examples: list[dict] = []
    for article_chunks in by_article.values():
        first = article_chunks[0]

        claim = headline(first["title"])
        for evidence in article_chunks[1:1 + HEADLINE_CHUNKS]:
            examples.append(make(claim, evidence, "supported", first, "headline"))
            unrelated = other_chunk(first)
            if unrelated:
                examples.append(make(claim, unrelated, "not_enough_evidence", first, "headline"))

        # Sentences as claims, the chunk they came from as the evidence.
        candidates = [(s, c) for c in article_chunks for s in sentences(c)]
        rng.shuffle(candidates)
        for sentence, chunk in candidates[:SENTENCES_PER_ARTICLE]:
            examples.append(make(sentence, chunk, "supported", chunk, "sentence"))
            unrelated = other_chunk(chunk)
            if unrelated:
                examples.append(make(sentence, unrelated, "not_enough_evidence", chunk, "sentence"))
            changed = change_number(sentence, rng)
            if changed:
                examples.append(make(changed, chunk, "contradicted", chunk, "sentence"))
    return examples


def overlap(claim: str, text: str) -> float:
    claim_words = set(WORD.findall(claim.lower()))
    if not claim_words:
        return 0.0
    return len(claim_words & set(WORD.findall(text.lower()))) / len(claim_words)


def label_candidates(chunks: list[dict], rng: random.Random) -> list[dict]:
    """Claim and evidence pairs from test articles, for you to label by hand."""
    test = [c for c in chunks if split_for(article_id(c)) == "test"]
    by_language = defaultdict(list)
    for chunk in test:
        by_language[chunk["language"]].append(chunk)

    rows = []
    for language, items in sorted(by_language.items()):
        claims = [(s, c) for c in items for s in sentences(c)]
        rng.shuffle(claims)
        count = 0
        for claim, source in claims:
            others = [c for c in items if article_id(c) != article_id(source)]
            if not others:
                break
            best = max(others, key=lambda c: overlap(claim, c["text"]))
            if overlap(claim, best["text"]) == 0:
                continue
            count += 1
            rows.append(
                {
                    "id": f"{language}-{count:03d}",
                    "language": language,
                    "claim": claim,
                    "evidence": best["text"],
                    "evidence_source": best["source"],
                    "label": "",
                }
            )
            if count >= LABEL_ROWS_PER_LANGUAGE:
                break
    return rows


def main() -> None:
    if not INPUT_PATH.exists():
        print("No crawled pages found. Run the crawler first.")
        return
    with open(INPUT_PATH, encoding="utf-8") as f:
        pages = [json.loads(line) for line in f if line.strip()]
    chunks = build_chunks(pages)
    rng = random.Random(SEED)

    examples = build_examples(chunks, rng)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(EXAMPLES_PATH, "w", encoding="utf-8") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(f"{len(pages)} articles -> {len(chunks)} chunks -> {len(examples)} examples")
    print("By label:   ", dict(Counter(e["label"] for e in examples)))
    print("By split:   ", dict(Counter(e["split"] for e in examples)))
    print("By language:", dict(Counter(e["language"] for e in examples)))
    print("By kind:    ", dict(Counter(e["kind"] for e in examples)))

    if LABEL_FILE.exists():
        print(f"\n{LABEL_FILE.name} already exists, so I left your labels untouched.")
        return
    rows = label_candidates(chunks, rng)
    with open(LABEL_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "language", "claim", "evidence", "evidence_source", "label"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} pairs to {LABEL_FILE} for you to label by hand.")


if __name__ == "__main__":
    main()