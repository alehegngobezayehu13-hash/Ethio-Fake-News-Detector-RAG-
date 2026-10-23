import time
from datetime import datetime, timezone

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from backend.app.fetcher import PAGE_TIMEOUT_MS

PAGE_DELAY_SECONDS = 1.5
MIN_POST_CHARS = 40

POSTS_JS = """
() => Array.from(document.querySelectorAll('.tgme_widget_message[data-post]')).map((message) => {
  const text = message.querySelector('.tgme_widget_message_text');
  const date = message.querySelector('.tgme_widget_message_date');
  const time = message.querySelector('.tgme_widget_message_date time');
  return {
    post: message.getAttribute('data-post') || '',
    text: text ? text.innerText : '',
    link: date ? date.href : '',
    time: time ? time.getAttribute('datetime') || '' : '',
  };
})
"""


def post_number(post: dict) -> int:
    """'tikvahethiopia/12345' -> 12345 (0 if it can't be read)."""
    tail = post.get("post", "").rsplit("/", 1)[-1]
    return int(tail) if tail.isdigit() else 0


def read_posts(username: str, limit: int) -> list[dict]:
    """The newest `limit` posts of a public channel, newest first."""
    posts: dict[int, dict] = {}
    before = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            while len(posts) < limit:
                url = f"https://t.me/s/{username}" + (f"?before={before}" if before else "")
                try:
                    page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
                    rows = page.evaluate(POSTS_JS)
                except PlaywrightError:
                    break
                added = 0
                for row in rows:
                    number = post_number(row)
                    if number and number not in posts:
                        posts[number] = row
                        added += 1
                if added == 0:
                    break  
                before = min(posts)
                time.sleep(PAGE_DELAY_SECONDS)
        finally:
            browser.close()
    return [posts[n] for n in sorted(posts, reverse=True)][:limit]


def post_record(post: dict, channel) -> dict | None:
    """Turn one post into the same record format the article crawler uses."""
    lines = [line.strip() for line in post.get("text", "").splitlines() if line.strip()]
    text = "\n".join(lines)
    if len(text) < MIN_POST_CHARS:
        return None  
    url = post.get("link") or f"https://t.me/{post['post']}"
    return {
        "url": url,
        "feed_url": url,
        "title": lines[0][:100],
        "text": text,
        "language": channel.language,
        "source": channel.name,
        "published": post.get("time", ""),
        "tags": ["telegram"],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }