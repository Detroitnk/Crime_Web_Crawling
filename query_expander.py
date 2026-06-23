"""
CrimeSignal-IN — query_expander.py
Takes user input (crime_type, region, extra_keywords) and generates
a list of 5-10 optimized search queries using the taxonomy and
complaint vocabulary.

Strategy: Mix crime keywords with complaint vocabulary markers,
platform names, and India-specific terms to find real victim posts,
not generic info pages.
"""

import random
from taxonomy import (
    COMPLAINT_VOCABULARY,
    PLATFORM_KEYWORDS,
    resolve_crime_input,
    get_region_keywords,
    CRIME_TAXONOMY,
)
from config import MAX_QUERIES_PER_RUN, COMPLAINT_MARKERS_PER_QUERY


# India-specific complaint portals and contexts
INDIA_COMPLAINT_CONTEXT = [
    "India victim experience",
    "India complaint filed",
    "India FIR registered",
    "cyber cell India",
    "consumer forum India",
    "lost money India scam",
]


def expand_queries(
    crime_type: str,
    region: str = "",
    extra_keywords: list[str] | None = None,
    max_queries: int = MAX_QUERIES_PER_RUN,
) -> list[str]:
    """
    Generate a diverse list of search queries optimized for finding
    real victim complaints, not generic info pages.

    Uses a MIX of quoted and unquoted queries since DDG may filter
    certain sensitive terms when quoted.

    Args:
        crime_type:     Free-text like "UPI fraud", "cyber crime", "sextortion"
        region:         Optional city/state like "Delhi", "Mumbai"
        extra_keywords: Additional user-provided terms
        max_queries:    Cap on number of queries returned

    Returns:
        List of search query strings (5-10 typically)
    """
    resolved = resolve_crime_input(crime_type)
    crime_keywords = resolved["keywords"]
    extra_keywords = extra_keywords or []

    # Build region component
    region_terms = get_region_keywords(region) if region else ["India"]
    primary_region = region if region else "India"

    # Strong complaint markers — words that indicate a real victim post
    strong_markers = [
        "scammed", "cheated", "lost money", "victim", "please help",
        "complaint", "FIR", "what should I do", "trapped",
    ]

    # Discussion platforms most likely to have victim posts
    victim_platforms = ["Reddit", "Quora", "r/LegalAdviceIndia", "consumercomplaints.in"]

    queries: list[str] = []

    # Select top multi-word crime keywords
    top_crime_kw = [kw for kw in crime_keywords if len(kw.split()) >= 2][:4]
    if not top_crime_kw:
        top_crime_kw = crime_keywords[:4]

    # ── Strategy 1: Unquoted crime keyword + complaint marker + region ──
    # Unquoted to avoid DDG filtering sensitive terms
    for kw in top_crime_kw[:3]:
        marker = random.choice(strong_markers)
        q = f"{kw} {marker} {primary_region}"
        queries.append(q)

    # ── Strategy 2: Crime keyword + discussion platform ──
    for kw in top_crime_kw[:2]:
        platform = random.choice(victim_platforms)
        q = f"{kw} {platform} India"
        queries.append(q)

    # ── Strategy 3: Crime keyword + India complaint context ──
    for kw in top_crime_kw[:2]:
        context = random.choice(INDIA_COMPLAINT_CONTEXT)
        q = f"{kw} {context}"
        if region:
            q += f" {region}"
        queries.append(q)

    # ── Strategy 4: Category-level broad victim search ──
    category_label = ""
    if resolved["category"] != "unknown":
        cat = CRIME_TAXONOMY.get(resolved["category"])
        if cat:
            category_label = cat["label"]
    if category_label:
        for suffix in [
            "victim complaint India",
            "scam report India",
        ]:
            q = f"{category_label} {suffix}"
            if region:
                q += f" {region}"
            queries.append(q)

    # ── Strategy 5: Direct crime_type as-is + complaint term ──
    # Simple query using the user's exact input
    q = f"{crime_type} complaint India"
    if region:
        q += f" {region}"
    queries.append(q)

    q = f"{crime_type} victim help India"
    queries.append(q)

    # ── Strategy 6: Extra user keywords ──
    for ek in extra_keywords:
        marker = random.choice(strong_markers)
        q = f"{ek} {marker} India"
        if region:
            q += f" {region}"
        queries.append(q)

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        q_norm = " ".join(q.split()).strip()
        if q_norm.lower() not in seen:
            seen.add(q_norm.lower())
            unique_queries.append(q_norm)

    # Shuffle and cap
    random.shuffle(unique_queries)
    return unique_queries[:max_queries]


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("Query Expander -- Self-Test")
    print("=" * 60)

    test_cases = [
        {"crime_type": "UPI fraud", "region": "Delhi"},
        {"crime_type": "cyber crime", "region": ""},
        {"crime_type": "sextortion", "region": "Mumbai"},
        {"crime_type": "loan app scam", "region": "Bangalore"},
    ]

    for tc in test_cases:
        print(f"\n> crime_type={tc['crime_type']!r}  region={tc['region']!r}")
        qs = expand_queries(tc["crime_type"], tc["region"])
        for i, q in enumerate(qs, 1):
            print(f"  {i}. {q}")
        print(f"  -> {len(qs)} queries generated")
