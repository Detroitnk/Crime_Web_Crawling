"""
CrimeSignal-IN — fetcher.py
Fetches raw HTML from a list of URLs using requests.
Handles timeouts, retries, and error logging.
"""

import logging
import time
import requests

from config import FETCH_TIMEOUT, FETCH_MAX_RETRIES, FETCH_USER_AGENT

logger = logging.getLogger(__name__)

# Headers to reduce bot detection and strip cookies/JS noise
REQUEST_HEADERS = {
    "User-Agent": FETCH_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
}

# Domains that block scraping or return useless content
SKIP_DOMAINS = [
    "youtube.com", "youtu.be",
    "facebook.com", "fb.com",
    "instagram.com",
    "tiktok.com",
    "play.google.com",
    "apps.apple.com",
]


def _should_skip(url: str) -> bool:
    """Check if URL is on the skip list."""
    url_lower = url.lower()
    return any(domain in url_lower for domain in SKIP_DOMAINS)


def _fetch_single(url: str, timeout: int = FETCH_TIMEOUT) -> dict:
    """
    Fetch a single URL with retry logic.

    Returns:
        {url, raw_html, status_code, fetch_success, error}
    """
    result = {
        "url": url,
        "raw_html": "",
        "status_code": 0,
        "fetch_success": False,
        "error": None,
    }

    if _should_skip(url):
        result["error"] = f"Skipped (blocked domain)"
        return result

    for attempt in range(1 + FETCH_MAX_RETRIES):
        try:
            resp = requests.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=timeout,
                allow_redirects=True,
                verify=True,
            )
            result["status_code"] = resp.status_code
            result["raw_html"] = resp.text
            result["fetch_success"] = resp.status_code == 200

            if resp.status_code == 200:
                return result
            else:
                result["error"] = f"HTTP {resp.status_code}"

        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection error"
        except requests.exceptions.TooManyRedirects:
            result["error"] = "Too many redirects"
        except Exception as e:
            result["error"] = str(e)

        # Wait briefly before retry
        if attempt < FETCH_MAX_RETRIES:
            time.sleep(0.5)

    return result


def fetch_urls(urls: list[str]) -> list[dict]:
    """
    Fetch raw HTML for a list of URLs.

    Args:
        urls: List of URL strings to fetch

    Returns:
        List of dicts:
            {
                "url":           str,
                "raw_html":      str,
                "status_code":   int,
                "fetch_success": bool,
                "error":         str or None,
            }
    """
    results: list[dict] = []
    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls):
        print(f"  [FETCH] [{i+1}/{len(urls)}] {url[:80]}...")
        result = _fetch_single(url)
        results.append(result)

        if result["fetch_success"]:
            success_count += 1
            html_size = len(result["raw_html"])
            logger.info(f"  OK: {url} ({html_size} chars)")
        else:
            fail_count += 1
            logger.warning(f"  FAIL: {url} - {result['error']}")
            print(f"    [WARN] {result['error']}")

    print(f"\n  [OK] Fetch complete: {success_count} success, {fail_count} failed out of {len(urls)}")
    return results


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    test_urls = [
        "https://www.geeksforgeeks.org/cybersecurity/what-is-phishing/",
        "https://cybercrime.gov.in/",
        "https://httpbin.org/status/404",  # will fail with 404
    ]

    print("=" * 60)
    print("Fetcher -- Self-Test")
    print("=" * 60)

    results = fetch_urls(test_urls)
    for r in results:
        status = "OK" if r["fetch_success"] else f"FAIL ({r['error']})"
        html_len = len(r["raw_html"])
        print(f"  {status:30s} | {html_len:>8} chars | {r['url'][:60]}")
