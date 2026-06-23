"""
CrimeSignal-IN — main.py
CLI entry point and pipeline orchestrator.
Runs: query_expander -> searcher -> fetcher -> extractor -> scorer -> ranker
Optional: AI layer (OpenRouter + Nemotron) for query expansion, classification, summarization.
"""

import sys
import os
import json
import argparse
import warnings
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Suppress duckduckgo_search rename warning
warnings.filterwarnings("ignore", message=".*duckduckgo_search.*renamed.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

from query_expander import expand_queries
from searcher import search_queries
from fetcher import fetch_urls
from extractor import extract_batch
from scorer import score_batch
from ranker import rank_results, format_results_for_display
from taxonomy import resolve_crime_input
from config import OUTPUT_DIR, TOP_N_RESULTS
import ai_layer


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="CrimeSignal-IN",
        description="AI-Assisted Public Crime Complaint Discovery & Trend Analysis for India",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --crime "UPI fraud" --region "Delhi" --top 5
  python main.py --crime "sextortion" --top 10 --save
  python main.py --crime "loan app scam" --region "Mumbai" --save --ai
        """,
    )
    parser.add_argument(
        "--crime", required=True, type=str,
        help="Crime type to search for (e.g., 'UPI fraud', 'sextortion', 'cyber crime')"
    )
    parser.add_argument(
        "--region", type=str, default="",
        help="Region/city to focus on (e.g., 'Delhi', 'Mumbai')"
    )
    parser.add_argument(
        "--keywords", type=str, default="",
        help="Extra comma-separated keywords to include in search"
    )
    parser.add_argument(
        "--top", type=int, default=TOP_N_RESULTS,
        help=f"Number of top results to display (default: {TOP_N_RESULTS})"
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save full results to outputs/ as JSON"
    )
    parser.add_argument(
        "--ai", action="store_true",
        help="Enable AI layer (OpenRouter + Nemotron) for enhanced query expansion, classification, and summarization"
    )
    return parser


def run_pipeline(
    crime: str,
    region: str = "",
    extra_keywords: list[str] | None = None,
    top_n: int = 10,
    save: bool = False,
    ai: bool = False,
) -> list[dict]:
    """
    Run the full CrimeSignal-IN pipeline.

    Args:
        crime:          Crime type string
        region:         Region/city string
        extra_keywords: Additional search terms
        top_n:          Number of results to return
        save:           Whether to save results to file
        ai:             Whether to enable AI analysis

    Returns:
        List of ranked result dicts
    """
    start_time = datetime.now()
    ai_enabled = False

    print("\n" + "=" * 75)
    print("  CrimeSignal-IN -- Crime Complaint Discovery System")
    print("=" * 75)
    print(f"  Crime Type:  {crime}")
    print(f"  Region:      {region or '(all India)'}")
    print(f"  Top Results: {top_n}")
    print(f"  AI Mode:     {'ON' if ai else 'OFF'}")
    print(f"  Timestamp:   {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)

    # ── AI availability check ──
    if ai:
        if ai_layer.is_available():
            ai_enabled = True
            print("\n  [AI] OpenRouter API key detected. AI features enabled.")
        else:
            print("\n  [AI WARN] OPENROUTER_API_KEY not set or openai SDK not installed.")
            print("  [AI WARN] Continuing without AI features. Set the key to enable.")
            ai_enabled = False

    # ── Step 0: Resolve crime type to taxonomy keywords ──
    resolved = resolve_crime_input(crime)
    keywords = resolved["keywords"]
    print(f"\n[STEP 0] Crime Resolution")
    print(f"  Category:  {resolved['category']}")
    print(f"  Subtypes:  {', '.join(resolved['subtypes']) if resolved['subtypes'] else 'direct match'}")
    print(f"  Keywords:  {len(keywords)} terms")

    # ── Step 1: Query Expansion ──
    print(f"\n[STEP 1] Query Expansion")
    print("-" * 40)
    queries = expand_queries(crime, region, extra_keywords)
    print(f"  Base queries: {len(queries)}")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. {q}")

    # AI-enhanced query expansion
    if ai_enabled:
        print(f"\n  [AI] Generating AI-enhanced queries...")
        ai_queries = ai_layer.expand_query_with_ai(crime, region)
        if ai_queries:
            # Deduplicate: merge AI queries with base queries
            existing_lower = {q.lower() for q in queries}
            new_ai = [q for q in ai_queries if q.lower() not in existing_lower]
            queries.extend(new_ai)
            print(f"  [AI] Added {len(new_ai)} AI-generated queries:")
            for i, q in enumerate(new_ai, 1):
                print(f"    AI-{i}. {q}")
        else:
            print(f"  [AI] No additional queries generated (API may be unavailable)")

    print(f"\n  -> {len(queries)} total queries")

    # ── Step 2: DuckDuckGo Search ──
    print(f"\n[STEP 2] Web Search (DuckDuckGo)")
    print("-" * 40)
    search_results = search_queries(queries, max_results_per_query=5)

    if not search_results:
        print("\n  [FAIL] No search results found. Try broader terms or check network.")
        return []

    # ── Step 3: Fetch HTML ──
    print(f"\n[STEP 3] Fetching Pages")
    print("-" * 40)
    urls = [r["url"] for r in search_results]
    fetched = fetch_urls(urls)

    # ── Step 4: Extract Text ──
    print(f"\n[STEP 4] Text Extraction")
    print("-" * 40)
    extracted = extract_batch(fetched)

    # ── Step 5: Score Results ──
    print(f"\n[STEP 5] Relevance Scoring")
    print("-" * 40)
    scored = score_batch(extracted, search_results, keywords, region)

    # ── Step 6: Rank ──
    print(f"\n[STEP 6] Ranking")
    print("-" * 40)
    ranked = rank_results(scored, top_n=top_n, min_score=0.05)

    # ── Step 7: AI Classification & Summarization ──
    if ai_enabled and ranked:
        print(f"\n[STEP 7] AI Analysis (Nemotron)")
        print("-" * 40)
        for i, result in enumerate(ranked):
            text = result.get("text", "") or result.get("snippet", "")
            title = result.get("title", "")
            rank = result.get("rank", i + 1)

            print(f"  [AI] Analyzing result #{rank}: {title[:50]}...")

            # Classify
            classification = ai_layer.classify_result(text, crime)
            result["ai_is_complaint"] = classification["is_complaint"]
            result["ai_confidence"] = classification["confidence"]
            result["ai_reason"] = classification["reason"]

            # Summarize (only if text is substantial)
            if len(text) > 100:
                summary = ai_layer.summarize_complaint(text)
                result["ai_summary"] = summary
            else:
                result["ai_summary"] = result.get("snippet", "")[:200]

            print(f"    Complaint: {'YES' if classification['is_complaint'] else 'NO'} "
                  f"(confidence: {classification['confidence']:.0%}) "
                  f"- {classification['reason']}")

        print(f"\n  [AI] Analysis complete for {len(ranked)} results")

    # ── Display results ──
    if ai_enabled and ranked:
        # Enhanced display with AI fields
        print(_format_ai_results(ranked))
    else:
        output_text = format_results_for_display(ranked)
        print(output_text)

    # ── Timing ──
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n  Pipeline completed in {elapsed:.1f} seconds")

    # ── Save Results ──
    if save and ranked:
        timestamp_str = start_time.strftime("%Y%m%d_%H%M%S")
        crime_slug = crime.replace(" ", "_").lower()
        filename = f"results_{crime_slug}_{timestamp_str}.json"
        filepath = OUTPUT_DIR / filename

        save_data = {
            "metadata": {
                "crime_type": crime,
                "region": region,
                "extra_keywords": extra_keywords or [],
                "top_n": top_n,
                "ai_enabled": ai_enabled,
                "timestamp": start_time.isoformat(),
                "elapsed_seconds": round(elapsed, 1),
                "total_search_results": len(search_results),
                "total_scored": len(scored),
                "total_ranked": len(ranked),
                "queries_used": queries,
            },
            "results": [
                {
                    "rank": r.get("rank"),
                    "composite_score": r.get("composite_score"),
                    "score_breakdown": r.get("score_breakdown"),
                    "url": r.get("url"),
                    "title": r.get("title"),
                    "snippet": r.get("snippet"),
                    "extraction_method": r.get("extraction_method"),
                    "char_count": r.get("char_count"),
                    "query_used": r.get("query_used"),
                    "text_preview": r.get("text", "")[:500],
                    # AI fields (present only when --ai used)
                    "ai_is_complaint": r.get("ai_is_complaint"),
                    "ai_confidence": r.get("ai_confidence"),
                    "ai_reason": r.get("ai_reason"),
                    "ai_summary": r.get("ai_summary"),
                }
                for r in ranked
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        print(f"\n  [SAVED] Results written to: {filepath}")

    return ranked


def _format_ai_results(ranked_items: list[dict]) -> str:
    """Format ranked results with AI analysis fields for CLI output."""
    if not ranked_items:
        return "  No results found."

    lines = []
    lines.append("")
    lines.append("=" * 75)
    lines.append("  RANKED RESULTS (AI-Enhanced)")
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

        # AI fields
        ai_complaint = item.get("ai_is_complaint", None)
        ai_conf = item.get("ai_confidence", None)
        ai_reason = item.get("ai_reason", "")
        ai_summary = item.get("ai_summary", "")

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

        # AI analysis
        if ai_complaint is not None:
            complaint_str = "YES" if ai_complaint else "NO"
            conf_str = f"{ai_conf:.0%}" if ai_conf is not None else "N/A"
            lines.append(f"  [AI] Complaint: {complaint_str} ({conf_str}) - {ai_reason}")
        if ai_summary:
            # Wrap summary to 70 chars
            if len(ai_summary) > 140:
                ai_summary = ai_summary[:137] + "..."
            lines.append(f"  [AI] Summary: {ai_summary}")

    lines.append(f"\n{'=' * 75}")
    lines.append(f"  Total ranked results: {len(ranked_items)}")
    lines.append(f"{'=' * 75}")

    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Parse extra keywords
    extra_keywords = None
    if args.keywords:
        extra_keywords = [kw.strip() for kw in args.keywords.split(",") if kw.strip()]

    results = run_pipeline(
        crime=args.crime,
        region=args.region,
        extra_keywords=extra_keywords,
        top_n=args.top,
        save=args.save,
        ai=args.ai,
    )

    if not results:
        print("\n  No relevant results found. Try different crime type or broader terms.")
        sys.exit(1)


if __name__ == "__main__":
    main()
