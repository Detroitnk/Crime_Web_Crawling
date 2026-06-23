# CrimeSignal-IN

**AI-Assisted Public Crime Complaint Discovery & Trend Analysis System for India**

---

## Table of Contents

1. [About the Project](#about-the-project)
2. [Libraries & Technologies Used](#libraries--technologies-used)
3. [Project Structure](#project-structure)
4. [Step-by-Step Setup & Run Guide](#step-by-step-setup--run-guide)
5. [CLI Flags Reference](#cli-flags-reference)
6. [Demo Scenarios](#demo-scenarios)
7. [How the Pipeline Works](#how-the-pipeline-works)
8. [Scoring Formula](#scoring-formula)
9. [AI Features (Optional)](#ai-features-optional)
10. [Supported Crime Types & Regions](#supported-crime-types--regions)
11. [Known Limitations](#known-limitations)
12. [License](#license)

---

## About the Project

Most crime victims in India never file an FIR. Instead, they describe their experiences on Reddit, Quora, Twitter/X, Facebook groups, complaint portals, and blogs. This hidden data contains real crime patterns that go undetected by official statistics.

**CrimeSignal-IN** is a CLI-based tool that automatically discovers and analyzes publicly available crime complaint data from the web. It searches the internet for victim posts, extracts and scores them for relevance, and optionally uses AI to classify and summarize the results.

---

## Libraries & Technologies Used

### Core Libraries (Required)

| Library | Version | Purpose | Why We Use It |
|---|---|---|---|
| **duckduckgo-search** | 8.1.1 | Web search API | Free, no API key needed, searches DuckDuckGo programmatically to find crime-related pages |
| **requests** | (built-in) | HTTP client | Downloads raw HTML from discovered URLs with custom headers, timeouts, and retry logic |
| **beautifulsoup4** | (built-in) | HTML parsing | Fallback text extractor — parses HTML `<p>` tags when trafilatura fails on a page |
| **trafilatura** | 2.1.0 | Web text extraction | Primary text extractor — strips boilerplate (ads, navbars, footers) and returns clean article text |
| **lxml** | 6.1.1 | XML/HTML parser | Fast HTML parser backend used internally by trafilatura and BeautifulSoup |

### AI Library (Optional)

| Library | Version | Purpose | Why We Use It |
|---|---|---|---|
| **openai** | 2.41.0 | OpenRouter API client | OpenAI-compatible SDK pointed at OpenRouter to call Nemotron 3 Ultra 550b (free model) for AI-powered query expansion, complaint classification, and text summarization |

### Standard Library Modules Used

| Module | Purpose |
|---|---|
| `argparse` | CLI argument parsing (--crime, --region, --top, --save, --ai) |
| `json` | Reading/writing JSON result files |
| `re` | Regular expressions for keyword matching and text cleaning |
| `os`, `sys` | Environment variables (API keys), path handling, encoding fixes |
| `pathlib` | Cross-platform file path management |
| `logging` | Structured error/warning logging throughout the pipeline |
| `warnings` | Suppressing third-party deprecation warnings |
| `datetime` | Timestamps for results and freshness scoring |
| `time` | Rate limiting between DuckDuckGo API calls |
| `random` | Query diversification (shuffling search strategies) |
| `hashlib` | URL deduplication via MD5 hashing |
| `urllib.parse` | URL domain extraction for trust scoring |

### AI Provider

| Detail | Value |
|---|---|
| **Provider** | OpenRouter (https://openrouter.ai) |
| **Model** | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| **Cost** | Free (zero charges on free tier) |
| **API Key** | Get one at https://openrouter.ai/keys |

---

## Project Structure

```
Web search project/
├── MEMORY.md                    — Session memory (progress tracker)
├── PROJECT_BLUEPRINT.md         — Original project design document
│
└── crimeSignal/                 — Main application package
    ├── __init__.py              — Package initializer
    ├── main.py                  — CLI entry point & pipeline orchestrator
    ├── taxonomy.py              — Crime type taxonomy (5 categories, 24 subtypes, keywords)
    ├── config.py                — All settings: scoring weights, timeouts, paths, AI config
    ├── query_expander.py        — Generates 8+ optimized search queries per crime type
    ├── searcher.py              — Runs DuckDuckGo searches with dedup & rate limiting
    ├── fetcher.py               — Downloads HTML pages with timeout, retry, domain skipping
    ├── extractor.py             — Extracts clean text (trafilatura primary, BS4 fallback)
    ├── scorer.py                — 5-component weighted relevance scoring engine
    ├── ranker.py                — Deduplication, threshold filtering, ranking, CLI formatting
    ├── ai_layer.py              — OpenRouter + Nemotron AI (optional, 4 functions)
    ├── combine_demo.py          — Utility to combine demo outputs into one JSON
    ├── README.md                — This file
    ├── memory/                  — Session memory storage directory
    └── outputs/                 — Saved JSON result files
        └── results_DEMO_FINAL.json
```

---

## Step-by-Step Setup & Run Guide

### Prerequisites

- **Python 3.10 or higher** installed on your system
- **Internet connection** (for web searches and page fetching)
- **Windows users:** Use `python -X utf8` to avoid encoding errors

### Step 1: Clone or Download the Project

Place the project folder anywhere on your system. For example:
```
C:\Users\yourname\Desktop\Web search project\
```

### Step 2: Open Terminal / Command Prompt

```bash
# Windows (PowerShell)
cd "C:\Users\yourname\Desktop\Web search project"

# Linux / macOS
cd ~/Desktop/Web\ search\ project
```

### Step 3: Install Required Libraries

Run this single command to install all dependencies:

```bash
pip install duckduckgo-search trafilatura beautifulsoup4 requests lxml
```

Expected output:
```
Successfully installed duckduckgo-search-8.1.1 trafilatura-2.1.0 lxml-6.1.1 ...
```

### Step 4: (Optional) Install AI Library

Only needed if you want AI-powered analysis with `--ai` flag:

```bash
pip install openai
```

### Step 5: Navigate to the Application Directory

```bash
cd crimeSignal
```

### Step 6: Run Your First Search

```bash
# Windows
python -X utf8 main.py --crime "UPI fraud" --region "Delhi" --top 5

# Linux / macOS
python main.py --crime "UPI fraud" --region "Delhi" --top 5
```

You should see output like:
```
===========================================================================
  CrimeSignal-IN -- Crime Complaint Discovery System
===========================================================================
  Crime Type:  UPI fraud
  Region:      Delhi
  Top Results: 5
  AI Mode:     OFF
  ...

[STEP 0] Crime Resolution
  Category:  cyber_crime
  ...

[STEP 1] Query Expansion
  1. UPI fraud complaint India Delhi
  2. UPI scam victim Delhi
  ...

[STEP 2] Web Search (DuckDuckGo)
  [SEARCH] [1/8] Searching: UPI fraud complaint India Delhi
  ...

[STEP 3-6] Fetching, Extracting, Scoring, Ranking...

===========================================================================
  RANKED RESULTS
===========================================================================
  #1  Score: 0.4387  [trafilatura, 103769 chars]
  Title:   Unified Payments Interface - Wikipedia
  URL:     https://en.m.wikipedia.org/wiki/Unified_Payments_Interface
  ...
```

### Step 7: Save Results to JSON

Add `--save` to write results to the `outputs/` folder:

```bash
python -X utf8 main.py --crime "UPI fraud" --region "Delhi" --top 5 --save
```

Results are saved to: `crimeSignal/outputs/results_upi_fraud_YYYYMMDD_HHMMSS.json`

### Step 8: (Optional) Enable AI Analysis

First, set your OpenRouter API key:

```powershell
# Windows PowerShell
$env:OPENROUTER_API_KEY = "your-key-from-openrouter.ai"
```

```bash
# Linux / macOS
export OPENROUTER_API_KEY="your-key-from-openrouter.ai"
```

Then run with `--ai`:

```bash
python -X utf8 main.py --crime "UPI fraud" --region "Delhi" --top 5 --save --ai
```

AI mode adds:
- AI-generated search queries (merged with base queries)
- Complaint classification (YES/NO with confidence %)
- 2-sentence text summary for each result

> **Get a free API key at:** https://openrouter.ai/keys
> The Nemotron 3 Ultra 550b model is completely free to use.

---

## CLI Flags Reference

| Flag | Required | Default | Description |
|---|---|---|---|
| `--crime` | **Yes** | — | Crime type to search for (e.g., `"UPI fraud"`, `"sextortion"`, `"loan app scam"`) |
| `--region` | No | all India | City or state to focus on (e.g., `"Delhi"`, `"Mumbai"`, `"Bangalore"`) |
| `--keywords` | No | — | Extra comma-separated keywords (e.g., `"PhonePe,Google Pay"`) |
| `--top` | No | 20 | Number of top results to display |
| `--save` | No | off | Save full results to `outputs/` directory as JSON |
| `--ai` | No | off | Enable AI analysis using Nemotron via OpenRouter |

---

## Demo Scenarios

### Scenario 1: UPI Fraud in Delhi (with AI)
```bash
python -X utf8 main.py --crime "UPI fraud" --region "Delhi" --top 5 --save --ai
```

### Scenario 2: Sextortion (free mode, all India)
```bash
python -X utf8 main.py --crime "sextortion" --top 5 --save
```

### Scenario 3: Loan App Scam (free mode, all India)
```bash
python -X utf8 main.py --crime "loan app scam" --top 5 --save
```

### More Examples
```bash
# Cyber crime in Mumbai with extra keywords
python -X utf8 main.py --crime "cyber crime" --region "Mumbai" --keywords "OTP,bank" --top 10 --save

# Investment scam in Bangalore
python -X utf8 main.py --crime "investment scam" --region "Bangalore" --top 5

# Phishing attacks (all India, AI enabled)
python -X utf8 main.py --crime "phishing" --top 5 --ai
```

---

## How the Pipeline Works

```
User Input (--crime, --region)
        |
        v
[STEP 0] Crime Resolution
        |  Maps user input to taxonomy keywords
        |  e.g., "UPI fraud" -> category: cyber_crime, keywords: 8 terms
        v
[STEP 1] Query Expansion
        |  Generates 8+ search queries using 6 strategies:
        |  - Crime keyword + complaint marker + region
        |  - Crime keyword + discussion platform (Reddit/Quora)
        |  - Crime keyword + India complaint context
        |  - Category-level broad search
        |  - Direct user input + complaint term
        |  - (Optional) AI-generated queries via Nemotron
        v
[STEP 2] Web Search (DuckDuckGo)
        |  Runs each query through DDG text search
        |  Deduplicates by URL, rate-limits to avoid blocking
        v
[STEP 3] Page Fetching
        |  Downloads HTML with requests library
        |  10-second timeout, 1 retry, skips blocked domains
        v
[STEP 4] Text Extraction
        |  Primary: trafilatura (strips boilerplate)
        |  Fallback: BeautifulSoup <p> tag extraction
        |  Minimum 100 chars to count as success
        v
[STEP 5] Relevance Scoring
        |  Scores each result on 5 dimensions (see formula below)
        v
[STEP 6] Ranking
        |  Deduplicates by URL hash
        |  Filters out scores below 0.05
        |  Sorts descending by composite score
        |  Returns top N results
        v
[STEP 7] AI Analysis (Optional, --ai flag)
        |  For each ranked result:
        |  - classify_result() -> is it a real complaint? (confidence %)
        |  - summarize_complaint() -> 2-sentence factual summary
        v
    CLI Output + JSON Save
```

---

## Scoring Formula

Each result is scored on 5 weighted components:

```
composite_score = keyword_match      * 0.35    (crime keyword density in text)
                + complaint_language  * 0.30    (victim vocabulary: "scammed", "cheated", "FIR")
                + location_match      * 0.15    (region/city mentioned in text)
                + freshness           * 0.10    (how recent the content is)
                + source_trust        * 0.10    (credibility of source domain)
```

### Source Trust Tiers

| Tier | Trust Score | Examples |
|---|---|---|
| Government | 0.95 | cybercrime.gov.in, india.gov.in |
| Complaint Portal | 0.85 | consumercomplaints.in, complainboard.in |
| News | 0.70 | ndtv.com, thehindu.com, indianexpress.com |
| Forum/Social | 0.55 | reddit.com, quora.com |
| Default | 0.40 | All other domains |

---

## AI Features (Optional)

When you run with `--ai`, CrimeSignal-IN calls NVIDIA Nemotron 3 Ultra 550b (free) via OpenRouter for:

| Function | What It Does | Token Limit |
|---|---|---|
| `expand_query_with_ai()` | Generates 5 additional AI-optimized search queries | 400 |
| `ask_followup_questions()` | Suggests 3 clarifying questions to narrow search | 200 |
| `summarize_complaint()` | Summarizes complaint text in 2 factual sentences | 150 |
| `classify_result()` | Classifies if a page is a real complaint (YES/NO + confidence) | 100 |

**Without `--ai`:** Everything works fine. The base pipeline uses zero API calls.

**With `--ai` but no API key:** Prints a warning and continues in free mode automatically.

---

## Supported Crime Types & Regions

### Crime Types (24 subtypes across 5 categories)

| Category | Subtypes |
|---|---|
| **Cyber Crime** | phishing, UPI fraud, OTP scam, loan app scam, investment scam, deepfake abuse, sextortion, fake customer care, Instagram fraud, WhatsApp fraud |
| **Sexual Crime** | sextortion, blackmail, harassment, non-consensual video |
| **Financial Fraud** | Ponzi scheme, fake job, fake rent, insurance fraud, lottery scam |
| **Harassment** | workplace, online, stalking, caste-based |
| **Abuse** | domestic, child, elder |

### Supported Regions

Delhi, Mumbai, Bangalore, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, Jaipur, Lucknow, Bhopal, Indore, Chandigarh, Kochi, Bhubaneswar, Patna, Ranchi, Guwahati

> You can also type any Indian city/state — the system will use it directly even if it's not in the built-in list.

---

## Known Limitations

| Limitation | Detail |
|---|---|
| DDG rate limiting | DuckDuckGo returns ~5 results per query batch |
| Government sites blocked | cybercrime.gov.in blocks automated requests (times out) |
| Sensitive term filtering | DDG may filter queries with terms like "sextortion" |
| Free AI model | Nemotron is free but may have slower response times |
| No persistent database | Results are saved as JSON files, not in a database |

---

## License

Academic research project. For educational purposes only.
