"""
CrimeSignal-IN — searcher.py
Takes a list of search queries and returns results from DuckDuckGo.
Output: list of dicts with url, title, snippet, query_used.
"""

import time
import logging
import warnings

# Suppress the "duckduckgo_search has been renamed to ddgs" RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

from duckduckgo_search import DDGS

from config import (
    SEARCH_MAX_RESULTS_PER_QUERY,
    SEARCH_REGION,
    SEARCH_SAFESEARCH,
    SEARCH_SLEEP_BETWEEN,
)

logger = logging.getLogger(__name__)


def search_queries(
    queries: list[str],
    max_results_per_query: int = SEARCH_MAX_RESULTS_PER_QUERY,
    region: str = SEARCH_REGION,
    safesearch: str = SEARCH_SAFESEARCH,
    sleep_between: float = SEARCH_SLEEP_BETWEEN,
) -> list[dict]:
    """
    Run each query through DuckDuckGo and collect results.

    Args:
        queries:                List of search query strings
        max_results_per_query:  Max results per query
        region:                 DDG region code (e.g. "in-en")
        safesearch:             "on", "moderate", or "off"
        sleep_between:          Seconds to wait between queries (rate limit)

    Returns:
        List of dicts:
            {
                "url":        str,
                "title":      str,
                "snippet":    str,
                "query_used": str,
            }
        Duplicates by URL are removed; first occurrence wins.
    """
    all_results: list[dict] = []
    seen_urls: set[str] = set()

    for i, query in enumerate(queries):
        logger.info(f"[{i+1}/{len(queries)}] Searching: {query!r}")
        print(f"  [SEARCH] [{i+1}/{len(queries)}] Searching: {query}")

        try:
            with DDGS() as ddgs:
                raw_results = list(
                    ddgs.text(
                        keywords=query,
                        region=region,
                        safesearch=safesearch,
                        max_results=max_results_per_query,
                    )
                )

            for r in raw_results:
                url = r.get("href", r.get("link", "")).strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                all_results.append({
                    "url":        url,
                    "title":      r.get("title", "").strip(),
                    "snippet":    r.get("body", r.get("snippet", "")).strip(),
                    "query_used": query,
                })

            logger.info(f"  → Got {len(raw_results)} raw, {len(all_results)} total unique")

        except Exception as e:
            logger.warning(f"  ⚠ Search failed for query {query!r}: {e}")
            print(f"  [WARN] Error: {e}")

        # Rate-limit between queries (skip after last)
        if i < len(queries) - 1 and sleep_between > 0:
            time.sleep(sleep_between)

    print(f"\n  [OK] Search complete: {len(all_results)} unique results from {len(queries)} queries")
    return all_results


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import json

    test_queries = [
        "UPI fraud scammed Delhi",
        "cyber crime victim complaint India Reddit",
    ]

    print("=" * 60)
    print("Searcher — Self-Test")
    print("=" * 60)

    results = search_queries(test_queries, max_results_per_query=5)
    print(f"\nTotal results: {len(results)}")
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"  Title:   {r['title']}")
        print(f"  URL:     {r['url']}")
        print(f"  Snippet: {r['snippet'][:120]}...")
        print(f"  Query:   {r['query_used']}")
