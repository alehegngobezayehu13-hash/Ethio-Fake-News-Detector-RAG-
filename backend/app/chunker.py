import hashlib
import json
import re
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
INPUT_PATH = DATA_DIR / "crawled" / "pages.jsonl"
OUTPUT_PATH = DATA_DIR / "processed" / "chunks.jsonl"

MAX_CHARS_LATIN = 700
MAX_CHARS_GEEZ = 450 
MIN_CHUNK_CHARS = 60
MAX_BLOCK_LINES = 40

DATE_LINE = re.compile(
    r"^(?:(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December) \d{1,2}(?:st|nd|rd|th)?, \d{4}|\d{1,2} \S+ \d{4})$"
)

# Page furniture that sits between a start line and an end line.
BLOCKS = [
    (re.compile(r"^Skip .+ and continue reading$"), re.compile(r"^End of ")),
    (re.compile(r"^Beeksisa bira darbii dubbisi"), re.compile(r"^Xumura beeksisaa")),
]


NOISE_PREFIXES = (
    "ዳታን በመቆጠብ", "የፎቶው ባለመብት", "የምስሉ መግለጫ", "ታትሟል",
    "Daataa qusachuuf", "MADDA SUURAA", "Ibsa waa'ee suuraa", "Maxxanfame", "Yeroo dubbisuu",
)


def block_end(lines: list[str], i: int) -> int | None:
    for start, end in BLOCKS:
        if start.match(lines[i]):
            for j in range(i + 1, min(i + MAX_BLOCK_LINES, len(lines))):
                if end.match(lines[j]):
                    return j
            return i  
    return None


def clean_article(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    kept: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line:
            i += 1
        elif line.startswith("Skip content"):
            i += 1
            while i + 1 < len(lines) and DATE_LINE.match(lines[i + 1]):
                i += 2
        elif (end := block_end(lines, i)) is not None:
            i = end + 1
        elif line.startswith(NOISE_PREFIXES):
            i += 1
        else:
            kept.append(line)
            i += 1

    while len(kept) >= 2 and DATE_LINE.match(kept[-1]):
        kept = kept[:-2]
    return "\n".join(kept)


def is_geez(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    geez = sum(1 for c in letters if "\u1200" <= c <= "\u137f")
    return geez / len(letters) > 0.5


def detect_language(text: str, hint: str) -> str:
    if is_geez(text):
        return hint if hint in ("am", "ti") else "am"
    return hint if hint in ("en", "om") else "en"


def pack(items: list[str], max_chars: int, sep: str) -> list[str]:
    """Join consecutive items into groups no longer than max_chars."""
    groups: list[str] = []
    current = ""
    for item in items:
        if current and len(current) + len(sep) + len(item) > max_chars:
            groups.append(current)
            current = item
        else:
            current = f"{current}{sep}{item}" if current else item
    if current:
        groups.append(current)
    return groups


def chunk_text(text: str, max_chars: int) -> list[str]:
    """Split text into paragraph-sized chunks, never cutting a sentence if avoidable."""
    pieces: list[str] = []
    for paragraph in text.split("\n"):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(paragraph) <= max_chars:
            pieces.append(paragraph)
            continue
        sentences = re.split(r"(?<=[.!?።፧])\s+", paragraph)
        cut = [s[k:k + max_chars] for s in sentences for k in range(0, len(s), max_chars)]
        pieces.extend(pack(cut, max_chars, " "))

    chunks = pack(pieces, max_chars, "\n")
    # Fold a tiny last chunk into the one before it instead of losing it.
    if len(chunks) > 1 and len(chunks[-1]) < MIN_CHUNK_CHARS:
        chunks[-2] = chunks[-2] + "\n" + chunks.pop()
    return [c for c in chunks if len(c) >= MIN_CHUNK_CHARS]


def build_chunks(pages: list[dict]) -> list[dict]:
    chunks: list[dict] = []
    for page in pages:
        text = clean_article(page["text"])
        language = detect_language(text, page.get("language", "en"))
        max_chars = MAX_CHARS_GEEZ if is_geez(text) else MAX_CHARS_LATIN
        page_id = hashlib.sha1(page["url"].encode("utf-8")).hexdigest()[:10]
        for n, chunk in enumerate(chunk_text(text, max_chars)):
            chunks.append(
                {
                    "id": f"{page_id}-{n}",
                    "url": page["url"],
                    "title": page["title"],
                    "source": page["source"],
                    "language": language,
                    "text": chunk,
                }
            )
    return chunks


def main() -> None:
    if not INPUT_PATH.exists():
        print(f"No crawled pages found at {INPUT_PATH}. Run the crawler first.")
        return
    with open(INPUT_PATH, encoding="utf-8") as f:
        pages = [json.loads(line) for line in f if line.strip()]

    chunks = build_chunks(pages)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"{len(pages)} articles -> {len(chunks)} chunks saved to {OUTPUT_PATH}")
    print("Chunks per language:", dict(Counter(c["language"] for c in chunks)))
    print("Chunks per source:  ", dict(Counter(c["source"] for c in chunks)))
    longest = max((len(c["text"]) for c in chunks), default=0)
    print("Longest chunk:", longest, "characters")


if __name__ == "__main__":
    main()