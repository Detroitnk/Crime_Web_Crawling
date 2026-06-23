"""
CrimeSignal-IN — scorer.py
Scores extracted text for crime complaint relevance using 5 weighted components.
All weights imported from config.py — never redefined here.
"""

import re
import logging
from urllib.parse import urlparse
from datetime import datetime

from config import (
    SCORING_WEIGHTS,
    SOURCE_TRUST,
    DEFAULT_SOURCE_TRUST,
)
from taxonomy import COMPLAINT_VOCABULARY

logger = logging.getLogger(__name__)

# Current year for freshness scoring
CURRENT_YEAR = datetime.now().year


def _normalize(value: float, floor: float = 0.0, ceiling: float = 1.0) -> float:
    """Clamp value between floor and ceiling."""
    return max(floor, min(ceiling, value))


def _score_keyword_match(text: str, keywords: list[str]) -> float:
    """
    Score based on crime keyword density in text.
    Count how many unique keywords appear, normalize by total keywords.
    """
    if not keywords or not text:
        return 0.0

    text_lower = text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in text_lower)
    raw = hits / len(keywords)
    return _normalize(raw)


def _score_complaint_language(text: str) -> float:
    """
    Score based on complaint vocabulary marker density.
    More markers = higher likelihood of a real victim post.
    """
    if not text:
        return 0.0

    text_lower = text.lower()
    hits = sum(1 for marker in COMPLAINT_VOCABULARY if marker.lower() in text_lower)

    # Normalize: 5+ markers = 1.0, scale linearly below that
    # Using 20 as the denominator to keep scores reasonable
    raw = hits / 20.0
    return _normalize(raw)


def _score_location_match(text: str, url: str, region: str) -> float:
    """
    Score based on region/location mention in text and URL.
    1.0 if region found in text, 0.5 if in URL/domain only, 0.0 if absent.
    """
    if not region:
        return 0.5  # no region specified = neutral score

    region_lower = region.strip().lower()

    # Check text
    if text and region_lower in text.lower():
        return 1.0

    # Check URL
    if url and region_lower in url.lower():
        return 0.5

    return 0.0


def _score_freshness(text: str, snippet: str = "") -> float:
    """
    Score based on year mentions in text content.
    Current year = 1.0, last year = 0.7, two years ago = 0.4, older = 0.1.
    """
    combined = f"{text} {snippet}".lower()

    if str(CURRENT_YEAR) in combined:
        return 1.0
    elif str(CURRENT_YEAR - 1) in combined:
        return 0.7
    elif str(CURRENT_YEAR - 2) in combined:
        return 0.4
    else:
        return 0.1


def _score_source_trust(url: str) -> float:
    """
    Score based on source domain credibility.
    Looks up domain in config.SOURCE_TRUST, falls back to DEFAULT_SOURCE_TRUST.
    """
    if not url:
        return DEFAULT_SOURCE_TRUST

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Strip www.
        if domain.startswith("www."):
            domain = domain[4:]

        # Direct lookup
        if domain in SOURCE_TRUST:
            return SOURCE_TRUST[domain]

        # Try parent domain (e.g., old.reddit.com -> reddit.com)
        parts = domain.split(".")
        if len(parts) > 2:
            parent = ".".join(parts[-2:])
            if parent in SOURCE_TRUST:
                return SOURCE_TRUST[parent]

    except Exception:
        pass

    return DEFAULT_SOURCE_TRUST


def score_result(
    extracted_item: dict,
    search_item: dict,
    keywords: list[str],
    region: str = "",
) -> dict:
    """
    Score a single extracted result for crime complaint relevance.

    Args:
        extracted_item: dict from extractor.py {url, text, extraction_method, char_count}
        search_item:    dict from searcher.py {url, title, snippet, query_used}
        keywords:       list of crime keywords used for this search
        region:         region/city string

    Returns:
        {
            "url":             str,
            "title":           str,
            "snippet":         str,
            "text":            str,
            "extraction_method": str,
            "char_count":      int,
            "query_used":      str,
            "composite_score": float (0.0 - 1.0),
            "score_breakdown": {
                "keyword":     float,
                "complaint":   float,
                "location":    float,
                "freshness":   float,
                "trust":       float,
            },
        }
    """
    url = extracted_item.get("url", "")
    text = extracted_item.get("text", "")
    snippet = search_item.get("snippet", "")

    # Use snippet as supplementary text if extraction failed or text is short
    scoring_text = text if text else snippet

    # Compute 5 sub-scores
    kw_score = _score_keyword_match(scoring_text, keywords)
    comp_score = _score_complaint_language(scoring_text)
    loc_score = _score_location_match(scoring_text, url, region)
    fresh_score = _score_freshness(scoring_text, snippet)
    trust_score = _score_source_trust(url)

    # Weighted composite
    composite = (
        kw_score    * SCORING_WEIGHTS["keyword_match"]
        + comp_score  * SCORING_WEIGHTS["complaint_language"]
        + loc_score   * SCORING_WEIGHTS["location_match"]
        + fresh_score * SCORING_WEIGHTS["freshness"]
        + trust_score * SCORING_WEIGHTS["source_trust"]
    )
    composite = _normalize(composite)

    return {
        "url":               url,
        "title":             search_item.get("title", ""),
        "snippet":           snippet,
        "text":              text,
        "extraction_method": extracted_item.get("extraction_method", "failed"),
        "char_count":        extracted_item.get("char_count", 0),
        "query_used":        search_item.get("query_used", ""),
        "composite_score":   round(composite, 4),
        "score_breakdown": {
            "keyword":   round(kw_score, 4),
            "complaint": round(comp_score, 4),
            "location":  round(loc_score, 4),
            "freshness": round(fresh_score, 4),
            "trust":     round(trust_score, 4),
        },
    }


def score_batch(
    extracted_items: list[dict],
    search_items: list[dict],
    keywords: list[str],
    region: str = "",
) -> list[dict]:
    """
    Score a batch of extracted results.

    Args:
        extracted_items: list from extractor.extract_batch()
        search_items:    list from searcher.search_queries()
        keywords:        crime keywords for scoring
        region:          region string

    Returns:
        List of scored result dicts
    """
    # Build URL -> search_item lookup
    search_lookup = {}
    for item in search_items:
        search_lookup[item["url"]] = item

    scored = []
    for i, ext_item in enumerate(extracted_items):
        url = ext_item["url"]
        search_item = search_lookup.get(url, {
            "url": url, "title": "", "snippet": "", "query_used": ""
        })

        result = score_result(ext_item, search_item, keywords, region)
        scored.append(result)

        logger.info(f"  Scored {url[:50]}: {result['composite_score']:.4f}")

    # Sort by score descending for preview
    scored.sort(key=lambda x: x["composite_score"], reverse=True)

    print(f"\n  [OK] Scoring complete: {len(scored)} results scored")
    if scored:
        top = scored[0]["composite_score"]
        bottom = scored[-1]["composite_score"]
        print(f"       Score range: {bottom:.4f} - {top:.4f}")

    return scored


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # Simulate test data
    test_extracted = {
        "url": "https://www.reddit.com/r/india/test",
        "text": "I was scammed via UPI fraud in Delhi. Lost money to a fake customer care number. "
                "I filed a complaint with cyber cell and FIR was registered. Please help, what should I do? "
                "This happened in 2026 and the fraudster used PhonePe.",
        "extraction_method": "trafilatura",
        "char_count": 250,
    }
    test_search = {
        "url": "https://www.reddit.com/r/india/test",
        "title": "UPI Fraud victim in Delhi - need help",
        "snippet": "I was scammed via UPI in Delhi...",
        "query_used": "UPI fraud scammed Delhi",
    }
    test_keywords = ["UPI fraud", "UPI scam", "PhonePe scam", "customer care scam"]

    print("=" * 60)
    print("Scorer -- Self-Test")
    print("=" * 60)

    result = score_result(test_extracted, test_search, test_keywords, region="Delhi")
    print(f"\n  Composite Score: {result['composite_score']}")
    print(f"  Breakdown:")
    for k, v in result["score_breakdown"].items():
        print(f"    {k:12s}: {v:.4f}")
