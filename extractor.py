"""
CrimeSignal-IN — extractor.py
Extracts clean text from raw HTML using trafilatura (primary)
and BeautifulSoup (fallback).
"""

import logging
import trafilatura
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 100  # minimum chars for trafilatura result to be accepted


def extract_text(fetched_item: dict) -> dict:
    """
    Extract readable text from a fetched HTML result.

    Args:
        fetched_item: dict from fetcher.py with keys:
            {url, raw_html, status_code, fetch_success, error}

    Returns:
        {
            "url":               str,
            "text":              str,
            "extraction_method": "trafilatura" | "beautifulsoup" | "failed",
            "char_count":        int,
        }
    """
    url = fetched_item.get("url", "")
    raw_html = fetched_item.get("raw_html", "")

    result = {
        "url": url,
        "text": "",
        "extraction_method": "failed",
        "char_count": 0,
    }

    # If fetch failed, nothing to extract
    if not fetched_item.get("fetch_success", False) or not raw_html:
        return result

    # ── Attempt 1: trafilatura ──
    try:
        extracted = trafilatura.extract(
            raw_html,
            include_comments=True,
            include_tables=True,
            no_fallback=False,
        )
        if extracted and len(extracted.strip()) >= MIN_TEXT_LENGTH:
            result["text"] = extracted.strip()
            result["extraction_method"] = "trafilatura"
            result["char_count"] = len(result["text"])
            logger.info(f"  trafilatura OK: {url} ({result['char_count']} chars)")
            return result
    except Exception as e:
        logger.debug(f"  trafilatura failed for {url}: {e}")

    # ── Attempt 2: BeautifulSoup fallback ──
    try:
        soup = BeautifulSoup(raw_html, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Extract text from paragraphs, headings, and list items
        text_parts = []
        for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "td", "blockquote"]):
            text = tag.get_text(separator=" ", strip=True)
            if text and len(text) > 20:  # skip tiny fragments
                text_parts.append(text)

        full_text = "\n".join(text_parts).strip()

        if full_text and len(full_text) >= MIN_TEXT_LENGTH:
            result["text"] = full_text
            result["extraction_method"] = "beautifulsoup"
            result["char_count"] = len(result["text"])
            logger.info(f"  BS4 OK: {url} ({result['char_count']} chars)")
            return result
    except Exception as e:
        logger.debug(f"  BeautifulSoup failed for {url}: {e}")

    # Both methods failed
    logger.warning(f"  Extraction failed for {url}")
    return result


def extract_batch(fetched_items: list[dict]) -> list[dict]:
    """
    Extract text from a batch of fetched items.

    Args:
        fetched_items: list of dicts from fetcher.fetch_urls()

    Returns:
        List of extraction result dicts
    """
    results = []
    method_counts = {"trafilatura": 0, "beautifulsoup": 0, "failed": 0}

    for i, item in enumerate(fetched_items):
        print(f"  [EXTRACT] [{i+1}/{len(fetched_items)}] {item['url'][:70]}...")
        extracted = extract_text(item)
        results.append(extracted)
        method_counts[extracted["extraction_method"]] += 1

    print(f"\n  [OK] Extraction complete: "
          f"{method_counts['trafilatura']} trafilatura, "
          f"{method_counts['beautifulsoup']} BS4, "
          f"{method_counts['failed']} failed")
    return results


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    from fetcher import fetch_urls

    test_urls = [
        "https://www.geeksforgeeks.org/cybersecurity/what-is-phishing/",
        "https://cybercrime.gov.in/",
    ]

    print("=" * 60)
    print("Extractor -- Self-Test")
    print("=" * 60)

    fetched = fetch_urls(test_urls)
    extracted = extract_batch(fetched)

    for e in extracted:
        print(f"\n  URL:    {e['url'][:60]}")
        print(f"  Method: {e['extraction_method']}")
        print(f"  Chars:  {e['char_count']}")
        if e['text']:
            print(f"  Preview: {e['text'][:200]}...")
