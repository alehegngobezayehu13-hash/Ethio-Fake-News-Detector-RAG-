"""Fetch web pages with a real browser and extract readable article text."""

import sys
from collections.abc import Callable
from dataclasses import dataclass

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

PAGE_TIMEOUT_MS = 15_000
MAX_CHARS = 20_000
MIN_LINE_CHARS = 15
BLOCKED_RESOURCES = {"image", "media", "font"}
NOISE_SELECTORS = "script, style, noscript, nav, header, footer, aside, form, iframe"

EXTRACT_JS = """
(noise) => {
  document.querySelectorAll(noise).forEach((el) => el.remove());
  const root = document.querySelector('article') || document.querySelector('main') || document.body;
  return root ? root.innerText : '';
}
"""


@dataclass
class FetchedPage:
    url: str
    title: str
    text: str
    requested_url: str = ""  


def clean_text(raw: str) -> str:
    """Drop blank and very short lines (menus, buttons) and cap the length."""
    lines = [line.strip() for line in raw.splitlines()]
    kept = [line for line in lines if len(line) >= MIN_LINE_CHARS]
    return "\n".join(kept)[:MAX_CHARS]


def fetch_pages(
    urls: list[str],
    url_filter: Callable[[str], bool] | None = None,
) -> list[FetchedPage]:
    """Open each URL in one browser session and return the pages that loaded.

    If url_filter is given, a page is kept only when the address it ends up on
    (after any redirects) passes the filter.
    """
    urls = [u for u in urls if u.startswith(("http://", "https://"))]
    pages: list[FetchedPage] = []
    if not urls:
        return pages

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in BLOCKED_RESOURCES
            else route.continue_(),
        )
        for url in urls:
            page = context.new_page()
            try:
                page.goto(url, timeout=PAGE_TIMEOUT_MS, wait_until="domcontentloaded")
                final_url = page.url
                if url_filter and not url_filter(final_url):
                    continue  
                title = page.title()
                text = clean_text(page.evaluate(EXTRACT_JS, NOISE_SELECTORS))
                if text:
                    pages.append(FetchedPage(final_url, title, text, requested_url=url))
            except PlaywrightError:
                pass  
            finally:
                page.close()
        browser.close()
    return pages


if __name__ == "__main__":
    test_urls = sys.argv[1:] or ["https://en.wikipedia.org/wiki/Addis_Ababa"]
    for fetched in fetch_pages(test_urls):
        print(fetched.url)
        print("Title:", fetched.title)
        print("Characters:", len(fetched.text))
        print(fetched.text[:500])