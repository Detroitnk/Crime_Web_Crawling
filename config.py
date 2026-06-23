"""
CrimeSignal-IN — config.py
Central configuration: scoring weights, search settings, timeouts, paths.
All tunable parameters live here.
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────
# Project paths
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MEMORY_DIR = BASE_DIR / "memory"
OUTPUT_DIR = BASE_DIR / "outputs"
MEMORY_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────
# AI Layer (OpenRouter + Nemotron)
# ──────────────────────────────────────────────
AI_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

# ──────────────────────────────────────────────
# Scoring weights (must sum to 1.0)
# ──────────────────────────────────────────────
SCORING_WEIGHTS = {
    "keyword_match":      0.35,   # crime keyword density
    "complaint_language":  0.30,   # complaint vocabulary markers
    "location_match":      0.15,   # region/city mention
    "freshness":           0.10,   # recency of content
    "source_trust":        0.10,   # credibility of source domain
}

# ──────────────────────────────────────────────
# Source trust scores (0.0 – 1.0)
# Higher = more trustworthy for crime complaint discovery
# ──────────────────────────────────────────────
SOURCE_TRUST = {
    # High trust — complaint-centric platforms
    "consumercomplaints.in":  0.95,
    "pgportal.gov.in":        0.95,
    "cybercrime.gov.in":      0.95,
    "nhrc.nic.in":            0.90,
    "consumerhelpline.gov.in": 0.90,

    # Moderate-high — community / discussion
    "reddit.com":             0.80,
    "quora.com":              0.75,
    "twitter.com":            0.70,
    "x.com":                  0.70,
    "facebook.com":           0.60,

    # News / media
    "ndtv.com":               0.75,
    "thehindu.com":           0.75,
    "indianexpress.com":      0.75,
    "timesofindia.indiatimes.com": 0.70,
    "hindustantimes.com":     0.70,
    "livemint.com":           0.70,
    "scroll.in":              0.70,
    "thewire.in":             0.70,

    # Medium — blogs / misc
    "medium.com":             0.55,
    "wordpress.com":          0.50,
    "blogspot.com":           0.45,
    "youtube.com":            0.50,
    "instagram.com":          0.45,
}
DEFAULT_SOURCE_TRUST = 0.40  # unknown domains

# ──────────────────────────────────────────────
# Search settings
# ──────────────────────────────────────────────
SEARCH_MAX_RESULTS_PER_QUERY = 10   # DuckDuckGo results per query string
SEARCH_REGION = "in-en"              # India, English
SEARCH_SAFESEARCH = "off"            # need crime content
SEARCH_SLEEP_BETWEEN = 1.5          # seconds between DDG calls (rate limit)

# ──────────────────────────────────────────────
# Fetch settings
# ──────────────────────────────────────────────
FETCH_TIMEOUT = 10        # seconds per request
FETCH_MAX_RETRIES = 1     # retry once on failure
FETCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

# ──────────────────────────────────────────────
# Query expansion settings
# ──────────────────────────────────────────────
MAX_QUERIES_PER_RUN = 8             # max queries generated per user input
COMPLAINT_MARKERS_PER_QUERY = 2     # how many complaint vocab words to inject

# ──────────────────────────────────────────────
# Ranking / output settings
# ──────────────────────────────────────────────
TOP_N_RESULTS = 20                  # default number of top results to show
MIN_SCORE_THRESHOLD = 0.15          # discard results below this score
DEDUP_SIMILARITY_THRESHOLD = 0.85   # URL similarity threshold for dedup

# ──────────────────────────────────────────────
# Freshness scoring (days → score)
# ──────────────────────────────────────────────
FRESHNESS_TIERS = {
    7:   1.0,   # last week
    30:  0.8,   # last month
    90:  0.6,   # last 3 months
    180: 0.4,   # last 6 months
    365: 0.2,   # last year
}
FRESHNESS_DEFAULT = 0.1  # older than a year or date unknown

# ──────────────────────────────────────────────
# AI layer (OpenRouter + Nemotron) — optional
# ──────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
AI_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
AI_MAX_TOKENS = 1024

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
LOG_LEVEL = "INFO"
