import argparse
import json
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


def host_in(url: str, domains: tuple[str, ...]) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) for d in domains)


def links_from_parsed(parsed, limit: int) -> list[str]:
    links: list[str] = []
    for entry in parsed.entries:
        link = entry.get("link")
        if link and link not in links:
            links.append(link)
        if len(links) >= limit:
            break
    return links


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


def parse_feed(feed: Feed):
    """Read a feed with a plain request first, then retry through the browser."""
    parsed = feedparser.parse(feed.url, agent=USER_AGENT)
    if not parsed.entries:
        text = fetch_feed_text(feed.url)
        if text:
            parsed = feedparser.parse(text)
    return parsed


def load_seen_urls(path: Path = OUTPUT_PATH) -> set[str]:
    """URLs already saved by earlier runs, so we never store an article twice."""
    seen: set[str] = set()
    if not path.exists():
        return seen
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                seen.add(json.loads(line)["url"])
            except (json.JSONDecodeError, KeyError):
                continue
    return seen


def append_records(records: list[dict], path: Path = OUTPUT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def crawl_feed(feed: Feed, per_feed: int, seen: set[str]) -> tuple[int, list[dict]]:
    """Read one feed and fetch its new articles. Returns (entries in feed, saved records)."""
    parsed = parse_feed(feed)
    links = [
        link
        for link in links_from_parsed(parsed, per_feed)
        if host_in(link, feed.domains) and link not in seen
    ]
    if not links:
        return len(parsed.entries), []

    pages = fetch_pages(links, url_filter=lambda url: host_in(url, feed.domains))
    fetched_at = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "url": page.url,
            "title": page.title,
            "text": page.text,
            "language": feed.language,
            "source": feed.name,
            "fetched_at": fetched_at,
        }
        for page in pages
        if page.url not in seen
    ]
    return len(parsed.entries), records


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl trusted news feeds.")
    parser.add_argument("--per-feed", type=int, default=10, help="max new articles per feed")
    args = parser.parse_args()

    seen = load_seen_urls()
    total = 0
    for feed in FEEDS:
        try:
            entries, records = crawl_feed(feed, args.per_feed, seen)
        except Exception as error:  
            print(f"WARNING {feed.name}: failed ({error})")
            continue
        if entries == 0:
            print(f"WARNING {feed.name}: no entries found, check the feed address")
            continue
        append_records(records)
        seen.update(r["url"] for r in records)
        total += len(records)
        print(f"{feed.name}: {entries} entries in feed, {len(records)} new articles saved")

    print(f"\nDone. {total} new articles saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()