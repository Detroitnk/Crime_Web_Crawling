"""
CrimeSignal-IN — Pipeline Test (Day 1)
Tests: query_expander -> searcher for crime="cyber crime" region="Delhi"
"""

import sys
import os
import json
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from query_expander import expand_queries
from searcher import search_queries


def run_pipeline_test():
    """End-to-end test: expand queries -> search -> print results."""
    crime_type = "cyber crime"
    region = "Delhi"

    print("=" * 70)
    print("  CrimeSignal-IN -- Day 1 Pipeline Test")
    print(f"  Crime: {crime_type!r}   Region: {region!r}")
    print(f"  Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Step 1: Expand queries
    print("\n[STEP 1] Query Expansion")
    print("-" * 40)
    queries = expand_queries(crime_type, region)
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    print(f"\n  -> {len(queries)} queries generated")

    # Step 2: Search
    print("\n[STEP 2] DuckDuckGo Search")
    print("-" * 40)
    results = search_queries(queries, max_results_per_query=5)

    # Step 3: Display results
    print("\n[STEP 3] Results")
    print("-" * 40)
    if not results:
        print("  [FAIL] No results found. Check network or DDG rate limits.")
        return

    for i, r in enumerate(results[:15], 1):  # show top 15
        print(f"\n  -- Result {i} --")
        print(f"  Title:   {r['title']}")
        print(f"  URL:     {r['url']}")
        snippet = r['snippet'][:150] + "..." if len(r['snippet']) > 150 else r['snippet']
        print(f"  Snippet: {snippet}")
        print(f"  Query:   {r['query_used']}")

    print(f"\n{'=' * 70}")
    print(f"  TOTAL UNIQUE RESULTS: {len(results)}")
    print(f"  QUERIES USED:         {len(queries)}")
    print(f"{'=' * 70}")

    # Save raw results for inspection
    output_file = f"outputs/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "crime_type": crime_type,
            "region": region,
            "queries": queries,
            "results": results,
            "total_results": len(results),
            "timestamp": datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    run_pipeline_test()
