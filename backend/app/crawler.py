import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import feedparser
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from backend.app.fetcher import PAGE_TIMEOUT_MS, fetch_pages
from backend.app.sources import FEEDS, Feed

OUTPUT_PATH = Path(__file__).resolve().parents[2] / "data" / "crawled" / "pages.jsonl"
USER_AGENT = "Mozilla/5.0 (compatible; EthioFakeNewsDetector/0.1)"
BATCH_SIZE = 20             
REQUEST_DELAY_SECONDS = 1.0 


def host_in(url: str, domains: tuple[str, ...]) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) for d in domains)


def feed_page_url(url: str, page: int) -> str:
    if page == 1:
        return url
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}paged={page}"


def fetch_feed_text(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            response = page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
            return response.text() if response and response.ok else ""
        except PlaywrightError:
            return ""
        finally:
            browser.close()


def parse_feed(url: str):
    parsed = feedparser.parse(url, agent=USER_AGENT)
    if not parsed.entries:
        text = fetch_feed_text(url)
        if text:
            parsed = feedparser.parse(text)
    return parsed


def entry_info(entry) -> dict:
    tags = [t.get("term", "") for t in entry.get("tags", []) if t.get("term")]
    return {
        "link": entry.get("link", ""),
        "published": entry.get("published", ""),
        "tags": tags,
    }


def read_feed(feed: Feed, max_pages: int) -> list[dict]:
    entries: list[dict] = []
    for page in range(1, (max_pages if feed.paged else 1) + 1):
        parsed = parse_feed(feed_page_url(feed.url, page))
        if not parsed.entries:
            break  
        entries.extend(entry_info(e) for e in parsed.entries)
        if page < max_pages and feed.paged:
            time.sleep(REQUEST_DELAY_SECONDS)
    return entries


def select_new(entries: list[dict], feed: Feed, limit: int, seen: set[str]) -> list[dict]:
    chosen: list[dict] = []
    links: set[str] = set()
    for entry in entries:
        link = entry["link"]
        if not link or link in seen or link in links or not host_in(link, feed.domains):
            continue
        links.add(link)
        chosen.append(entry)
        if len(chosen) >= limit:
            break
    return chosen


def load_seen_urls(path: Path = OUTPUT_PATH) -> set[str]:
    seen: set[str] = set()
    if not path.exists():
        return seen
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            seen.add(record.get("url", ""))
            seen.add(record.get("feed_url", ""))
    seen.discard("")
    return seen


def append_records(records: list[dict], path: Path = OUTPUT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def crawl_feed(feed: Feed, per_feed: int, max_pages: int, seen: set[str]) -> tuple[int, int]:
    entries = read_feed(feed, max_pages)
    todo = select_new(entries, feed, per_feed, seen)
    saved = 0
    for start in range(0, len(todo), BATCH_SIZE):
        batch = todo[start:start + BATCH_SIZE]
        info = {e["link"]: e for e in batch}
        pages = fetch_pages(
            [e["link"] for e in batch],
            url_filter=lambda url: host_in(url, feed.domains),
        )
        fetched_at = datetime.now(timezone.utc).isoformat()
        records = []
        for page in pages:
            if page.url in seen:
                continue
            extra = info.get(page.requested_url, {})
            records.append(
                {
                    "url": page.url,
                    "feed_url": page.requested_url,
                    "title": page.title,
                    "text": page.text,
                    "language": feed.language,
                    "source": feed.name,
                    "published": extra.get("published", ""),
                    "tags": extra.get("tags", []),
                    "fetched_at": fetched_at,
                }
            )
        append_records(records)
        for record in records:
            seen.add(record["url"])
            seen.add(record["feed_url"])
        saved += len(records)
        print(f"  {feed.name}: {saved} saved so far ({min(start + BATCH_SIZE, len(todo))}/{len(todo)} tried)")
    return len(entries), saved


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl trusted news feeds.")
    parser.add_argument("--per-feed", type=int, default=10, help="max new articles per feed")
    parser.add_argument("--max-pages", type=int, default=5, help="feed pages to read for pageable feeds")
    args = parser.parse_args()

    seen = load_seen_urls()
    total = 0
    for feed in FEEDS:
        try:
            entries, saved = crawl_feed(feed, args.per_feed, args.max_pages, seen)
        except Exception as error:  
            print(f"WARNING {feed.name}: failed ({error})")
            continue
        if entries == 0:
            print(f"WARNING {feed.name}: no entries found, check the feed address")
            continue
        total += saved
        print(f"{feed.name}: {entries} entries in feed, {saved} new articles saved")

    print(f"\nDone. {total} new articles saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()