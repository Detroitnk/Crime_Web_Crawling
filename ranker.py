"""
CrimeSignal-IN — ranker.py
Takes scored results, deduplicates, filters, and returns top N ranked results.
"""

import logging
from config import MIN_SCORE_THRESHOLD, TOP_N_RESULTS

logger = logging.getLogger(__name__)


def rank_results(
    scored_items: list[dict],
    top_n: int = TOP_N_RESULTS,
    min_score: float = MIN_SCORE_THRESHOLD,
) -> list[dict]:
    """
    Rank, deduplicate, and filter scored results.

    Args:
        scored_items: list of dicts from scorer.score_batch()
        top_n:        max number of results to return
        min_score:    minimum composite_score threshold

    Returns:
        List of top_n result dicts, each with 'rank' field added (1-indexed).
        Sorted by composite_score descending.
    """
    if not scored_items:
        print("  [RANK] No results to rank.")
        return []

    # ── Step 1: Deduplicate by URL ──
    seen_urls: set[str] = set()
    unique_items: list[dict] = []
    for item in scored_items:
        url = item.get("url", "").strip().rstrip("/")
        url_key = url.lower()
        if url_key not in seen_urls:
            seen_urls.add(url_key)
            unique_items.append(item)

    deduped_count = len(scored_items) - len(unique_items)
    if deduped_count > 0:
        logger.info(f"  Removed {deduped_count} duplicate URLs")

    # ── Step 2: Filter by minimum score ──
    filtered = [
        item for item in unique_items
        if item.get("composite_score", 0) >= min_score
    ]
    filtered_count = len(unique_items) - len(filtered)
    if filtered_count > 0:
        logger.info(f"  Filtered {filtered_count} results below score {min_score}")

    # ── Step 3: Sort by composite_score descending ──
    filtered.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

    # ── Step 4: Take top N and add rank ──
    top_results = filtered[:top_n]
    for i, item in enumerate(top_results, 1):
        item["rank"] = i

    print(f"  [RANK] {len(scored_items)} scored -> "
          f"{len(unique_items)} unique -> "
          f"{len(filtered)} above threshold -> "
          f"{len(top_results)} returned (top {top_n})")

    return top_results


def format_results_for_display(ranked_items: list[dict]) -> str:
    """
    Format ranked results into a clean, readable string for CLI output.

    Args:
        ranked_items: list from rank_results()

    Returns:
        Formatted string ready to print
    """
    if not ranked_items:
        return "  No results found matching your criteria."

    lines = []
    lines.append("")
    lines.append("=" * 75)
    lines.append("  RANKED RESULTS")
    lines.append("=" * 75)

    for item in ranked_items:
        rank = item.get("rank", "?")
        score = item.get("composite_score", 0)
        url = item.get("url", "")
        title = item.get("title", "No title")
        snippet = item.get("snippet", "")
        method = item.get("extraction_method", "?")
        chars = item.get("char_count", 0)
        breakdown = item.get("score_breakdown", {})

        # Truncate long fields
        if len(title) > 70:
            title = title[:67] + "..."
        if len(snippet) > 120:
            snippet = snippet[:117] + "..."

        lines.append(f"\n  #{rank}  Score: {score:.4f}  [{method}, {chars} chars]")
        lines.append(f"  Title:   {title}")
        lines.append(f"  URL:     {url}")
        lines.append(f"  Snippet: {snippet}")

        # Score breakdown
        bd = "  Scores:  "
        bd += " | ".join(f"{k}={v:.2f}" for k, v in breakdown.items())
        lines.append(bd)

    lines.append(f"\n{'=' * 75}")
    lines.append(f"  Total ranked results: {len(ranked_items)}")
    lines.append(f"{'=' * 75}")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────
if __name__ == "__main__":
    # Simulate scored data
    test_data = [
        {
            "url": "https://reddit.com/r/india/post1",
            "title": "UPI Fraud in Delhi",
            "snippet": "I was scammed via UPI...",
            "text": "Full text here...",
            "extraction_method": "trafilatura",
            "char_count": 500,
            "query_used": "UPI fraud Delhi",
            "composite_score": 0.72,
            "score_breakdown": {"keyword": 0.8, "complaint": 0.9, "location": 1.0, "freshness": 1.0, "trust": 0.8},
        },
        {
            "url": "https://en.wikipedia.org/wiki/Phishing",
            "title": "Phishing - Wikipedia",
            "snippet": "Phishing is a form of...",
            "text": "Wikipedia article...",
            "extraction_method": "trafilatura",
            "char_count": 3000,
            "query_used": "phishing India",
            "composite_score": 0.18,
            "score_breakdown": {"keyword": 0.3, "complaint": 0.0, "location": 0.0, "freshness": 0.1, "trust": 0.4},
        },
        {
            "url": "https://reddit.com/r/india/post1",  # duplicate
            "title": "UPI Fraud in Delhi (dupe)",
            "snippet": "Same post...",
            "text": "Same...",
            "extraction_method": "trafilatura",
            "char_count": 500,
            "query_used": "UPI fraud",
            "composite_score": 0.72,
            "score_breakdown": {"keyword": 0.8, "complaint": 0.9, "location": 1.0, "freshness": 1.0, "trust": 0.8},
        },
        {
            "url": "https://example.com/low",
            "title": "Low score result",
            "snippet": "Irrelevant...",
            "text": "",
            "extraction_method": "failed",
            "char_count": 0,
            "query_used": "test",
            "composite_score": 0.02,
            "score_breakdown": {"keyword": 0.0, "complaint": 0.0, "location": 0.0, "freshness": 0.1, "trust": 0.4},
        },
    ]

    print("=" * 60)
    print("Ranker -- Self-Test")
    print("=" * 60)

    ranked = rank_results(test_data, top_n=5)
    output = format_results_for_display(ranked)
    print(output)
