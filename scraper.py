from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

TARGET_URLS = [
    "https://versebyverseministry.org/bible-studies/category/old-testament-books?category=old-testament-books",
    "https://versebyverseministry.org/bible-studies/category/new-testament-books?category=old-testament-books",
]

PDF_DIR = Path("./data/pdfs")
MANIFEST_PATH = PDF_DIR / "manifest.json"


def sanitize_filename(url: str) -> str:
    """Create a filesystem-safe filename from a URL."""
    parsed = urlparse(url)
    name = Path(parsed.path).name or "download.pdf"
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    return name


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {}


def save_manifest(data: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def extract_pdf_links_from_html(html: str, base_url: str) -> Set[str]:
    """Extract PDF links from HTML content, including anchors and iframe/embed sources."""
    soup = BeautifulSoup(html, "html.parser")
    pdf_urls: Set[str] = set()

    def maybe_add(value: str | None) -> None:
        if value:
            pdf_urls.add(urljoin(base_url, value))

    for tag in soup.find_all(["a", "link"]):
        href = tag.get("href")
        if href and "pdf" in href.lower():
            maybe_add(href)

    for tag in soup.find_all(["iframe", "embed", "object"]):
        src = tag.get("src") or tag.get("data")
        if src and "pdf" in src.lower():
            maybe_add(src)

    return pdf_urls


def discover_pdf_urls(page, url: str) -> Set[str]:
    """Visit a page and collect PDF URLs from DOM and network responses."""
    pdf_urls: Set[str] = set()

    def on_response(response) -> None:
        content_type = response.headers.get("content-type", "").lower()
        if "pdf" in content_type:
            pdf_urls.add(response.url)

    page.on("response", on_response)
    page.goto(url, wait_until="networkidle")

    pdf_urls.update(extract_pdf_links_from_html(page.content(), page.url))

    for frame in page.frames:
        try:
            frame_html = frame.content()
            pdf_urls.update(extract_pdf_links_from_html(frame_html, frame.url))
        except Exception:
            # Some frames may be cross-origin; ignore failures.
            continue

    return pdf_urls


def download_pdf(request_context, url: str, dest_path: Path) -> None:
    response = request_context.get(url)
    if response.ok:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(response.body())
    else:
        raise RuntimeError(f"Failed to download {url} (status: {response.status})")


def ensure_unique_filename(existing: Iterable[str], desired: str) -> str:
    if desired not in existing:
        return desired
    stem = Path(desired).stem
    suffix = Path(desired).suffix
    counter = 1
    while True:
        candidate = f"{stem}_{counter}{suffix}"
        if candidate not in existing:
            return candidate
        counter += 1


def scrape() -> None:
    manifest = load_manifest()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        request_context = playwright.request.new_context()
        page = context.new_page()

        for target_url in TARGET_URLS:
            pdf_urls = discover_pdf_urls(page, target_url)
            for pdf_url in pdf_urls:
                filename = sanitize_filename(pdf_url)
                filename = ensure_unique_filename(manifest.keys(), filename)
                if (PDF_DIR / filename).exists():
                    # Already downloaded
                    continue
                try:
                    download_pdf(request_context, pdf_url, PDF_DIR / filename)
                    manifest[filename] = pdf_url
                except Exception:
                    # Skip problematic downloads to keep pipeline moving.
                    continue

        save_manifest(manifest)
        page.close()
        context.close()
        browser.close()


if __name__ == "__main__":
    scrape()
