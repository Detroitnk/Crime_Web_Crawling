"""
CrimeSignal-IN — Combine demo outputs into results_DEMO_FINAL.json
"""

import sys
import os
import json
import glob
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def combine_demo_results():
    """Combine all demo result JSON files into a single final output."""
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")

    # Find the latest result file for each crime type
    crime_types = ["upi_fraud", "sextortion", "loan_app_scam"]
    combined = {
        "title": "CrimeSignal-IN Demo Results",
        "generated": datetime.now().isoformat(),
        "scenarios": [],
    }

    for crime in crime_types:
        pattern = os.path.join(output_dir, f"results_{crime}_*.json")
        files = sorted(glob.glob(pattern))
        if files:
            latest = files[-1]  # most recent
            with open(latest, "r", encoding="utf-8") as f:
                data = json.load(f)
            combined["scenarios"].append({
                "crime_type": crime.replace("_", " "),
                "source_file": os.path.basename(latest),
                "data": data,
            })
            print(f"  Added: {os.path.basename(latest)}")
        else:
            print(f"  [WARN] No results found for {crime}")

    # Save combined
    output_path = os.path.join(output_dir, "results_DEMO_FINAL.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print(f"\n  [SAVED] Combined demo: {output_path}")
    print(f"  Scenarios: {len(combined['scenarios'])}")


if __name__ == "__main__":
    combine_demo_results()
