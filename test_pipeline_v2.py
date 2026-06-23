"""
CrimeSignal-IN — Pipeline Test v2 (Day 1)
Tests with more specific crime types to show query quality.
"""

import sys
import os
import json
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from query_expander import expand_queries
from searcher import search_queries


def run_test(crime_type: str, region: str):
    """Run a single pipeline test."""
    print(f"\n{'=' * 70}")
    print(f"  TEST: crime={crime_type!r}  region={region!r}")
    print(f"{'=' * 70}")

    queries = expand_queries(crime_type, region)
    print(f"\n  Queries ({len(queries)}):")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. {q}")

    results = search_queries(queries, max_results_per_query=5)

    print(f"\n  Results ({len(results)}):")
    for i, r in enumerate(results[:10], 1):
        print(f"\n    [{i}] {r['title']}")
        print(f"        {r['url']}")
        snippet = r['snippet'][:120] + "..." if len(r['snippet']) > 120 else r['snippet']
        print(f"        {snippet}")

    # Save
    output_file = f"outputs/test_{crime_type.replace(' ','_')}_{datetime.now().strftime('%H%M%S')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "crime_type": crime_type,
            "region": region,
            "queries": queries,
            "results": results,
            "total": len(results),
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved: {output_file}")
    return len(results)


if __name__ == "__main__":
    print("CrimeSignal-IN -- Multi-Scenario Pipeline Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    scenarios = [
        ("UPI fraud", "Delhi"),
        ("loan app scam", ""),
        ("sextortion", "Mumbai"),
    ]

    total = 0
    for crime, region in scenarios:
        total += run_test(crime, region)

    print(f"\n{'=' * 70}")
    print(f"  ALL TESTS COMPLETE. Total results across all scenarios: {total}")
    print(f"{'=' * 70}")
