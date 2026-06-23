"""
CrimeSignal-IN — ai_layer.py
OpenRouter-powered AI functions (Nemotron 3 Ultra 550b) for query expansion,
classification, summarization, and follow-up question generation.

All calls use max_tokens <= 400 to minimize API cost.
Falls back gracefully when API key is missing or calls fail.
Uses OpenRouter API (OpenAI-compatible) with OPENROUTER_API_KEY env var.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# Lazy-load the openai SDK to avoid import errors when not installed
_client = None

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _get_client():
    """Get or create the OpenRouter client. Returns None if unavailable."""
    global _client
    if _client is not None:
        return _client

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI
        _client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=api_key,
        )
        return _client
    except ImportError:
        logger.warning("openai SDK not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.warning(f"Failed to create OpenRouter client: {e}")
        return None


def is_available() -> bool:
    """Check if the AI layer is available (API key set and SDK installed)."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return False
    try:
        from openai import OpenAI
        return True
    except ImportError:
        return False


def _call_ai(system_prompt: str, user_prompt: str, max_tokens: int = 400) -> str:
    """
    Make a single OpenRouter API call using Nemotron 3 Ultra 550b.

    Args:
        system_prompt: System instruction
        user_prompt:   User message
        max_tokens:    Max response tokens

    Returns:
        Response text string. Empty string on failure.
    """
    client = _get_client()
    if client is None:
        return ""

    try:
        from config import AI_MODEL
        response = client.chat.completions.create(
            model=AI_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        # Extract text from response
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return ""
    except Exception as e:
        logger.warning(f"OpenRouter API call failed: {e}")
        print(f"    [AI WARN] API call failed: {e}")
        return ""


# ──────────────────────────────────────────────────────
# Function a: AI-powered query expansion
# ──────────────────────────────────────────────────────
def expand_query_with_ai(
    crime_type: str,
    region: str = "",
    context: str = "",
) -> list[str]:
    """
    Use Nemotron to generate 5 optimized search queries for finding
    real victim complaints.

    Args:
        crime_type: Crime type string (e.g., "UPI fraud")
        region:     Region/city (e.g., "Delhi")
        context:    Extra context from user

    Returns:
        List of search query strings. Empty list on failure.
    """
    system = (
        "You are a crime research assistant for India. "
        "Output only a JSON array of strings. No explanation."
    )
    user = (
        f"Generate 5 DuckDuckGo search queries to find real victim complaints "
        f"in India about: {crime_type}. "
        f"Region: {region or 'any'}. "
        f"Extra context: {context or 'none'}. "
        f"Queries must sound like victim posts or complaint forum threads. "
        f"Output only a JSON array."
    )

    raw = _call_ai(system, user, max_tokens=400)
    if not raw:
        return []

    try:
        # Try to parse JSON array from response
        # Handle cases where the model wraps in markdown code blocks
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            )
        result = json.loads(cleaned)
        if isinstance(result, list):
            return [str(q).strip() for q in result if q]
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse AI query expansion: {e}")
        print(f"    [AI WARN] Could not parse query expansion response")

    return []


# ──────────────────────────────────────────────────────
# Function b: Follow-up questions
# ──────────────────────────────────────────────────────
def ask_followup_questions(crime_type: str) -> list[str]:
    """
    Generate 3 clarifying questions to help narrow down search.

    Args:
        crime_type: Crime type string

    Returns:
        List of 3 question strings.
    """
    defaults = [
        f"In which city/state did the {crime_type} occur?",
        f"On which platform (WhatsApp, UPI app, website) did it happen?",
        f"What is the approximate age group of the victim?",
    ]

    system = (
        "You are a crime intelligence assistant. "
        "Output only a JSON array of 3 short question strings. No explanation."
    )
    user = (
        f"What 3 clarifying questions would help narrow down a search for "
        f"'{crime_type}' complaints in India? "
        f"Focus on region, platform, and victim profile."
    )

    raw = _call_ai(system, user, max_tokens=200)
    if not raw:
        return defaults

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            )
        result = json.loads(cleaned)
        if isinstance(result, list) and len(result) >= 3:
            return [str(q).strip() for q in result[:3]]
    except json.JSONDecodeError:
        logger.warning("Failed to parse AI follow-up questions")

    return defaults


# ──────────────────────────────────────────────────────
# Function c: Complaint summarization
# ──────────────────────────────────────────────────────
def summarize_complaint(text: str) -> str:
    """
    Summarize complaint text in 2 factual sentences.

    Args:
        text: Full extracted text (will be truncated to 1500 chars)

    Returns:
        Summary string. Falls back to first 200 chars on failure.
    """
    if not text:
        return ""

    truncated = text[:1500]
    fallback = text[:200].strip() + "..."

    system = (
        "You summarize crime complaint text from India in 2 sentences. "
        "Be factual. No advice."
    )

    raw = _call_ai(system, truncated, max_tokens=150)
    if raw:
        return raw
    return fallback


# ──────────────────────────────────────────────────────
# Function d: Result classification
# ──────────────────────────────────────────────────────
def classify_result(text: str, crime_type: str) -> dict:
    """
    Classify whether extracted text is a real crime complaint.

    Args:
        text:       Extracted text (truncated to 800 chars)
        crime_type: Crime type being searched for

    Returns:
        {
            "is_complaint": bool,
            "confidence":   float (0.0 - 1.0),
            "reason":       str (under 10 words),
        }
    """
    fail_result = {
        "is_complaint": False,
        "confidence": 0.0,
        "reason": "classification unavailable",
    }

    if not text:
        return fail_result

    truncated = text[:800]

    system = (
        "You classify web page text. Output only JSON: "
        '{"is_complaint": bool, "confidence": float 0-1, '
        '"reason": string under 10 words}. No other output.'
    )
    user = (
        f"Crime type being searched: {crime_type}\n\n"
        f"Text to classify:\n{truncated}"
    )

    raw = _call_ai(system, user, max_tokens=100)
    if not raw:
        return fail_result

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(
                line for line in lines
                if not line.strip().startswith("```")
            )
        result = json.loads(cleaned)
        return {
            "is_complaint": bool(result.get("is_complaint", False)),
            "confidence": float(result.get("confidence", 0.0)),
            "reason": str(result.get("reason", "unknown"))[:50],
        }
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"Failed to parse AI classification: {e}")
        return fail_result


# ──────────────────────────────────────────────────────
# Quick self-test
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 60)
    print("AI Layer -- Self-Test (OpenRouter + Nemotron)")
    print("=" * 60)

    print(f"\n  API Available: {is_available()}")

    if not is_available():
        print("  Set OPENROUTER_API_KEY environment variable to test AI functions.")
        print("  Showing fallback behavior instead:\n")

        # Test fallbacks
        qs = expand_query_with_ai("UPI fraud", "Delhi")
        print(f"  expand_query_with_ai: {qs}")

        fq = ask_followup_questions("UPI fraud")
        print(f"  ask_followup_questions: {fq}")

        summary = summarize_complaint("I was cheated via UPI payment in Delhi.")
        print(f"  summarize_complaint: {summary}")

        cls = classify_result("I lost money to a UPI fraud scammer.", "UPI fraud")
        print(f"  classify_result: {cls}")
    else:
        print("  Testing with live API...\n")

        print("  [1] Query Expansion:")
        qs = expand_query_with_ai("UPI fraud", "Delhi")
        for i, q in enumerate(qs, 1):
            print(f"      {i}. {q}")

        print("\n  [2] Follow-up Questions:")
        fq = ask_followup_questions("UPI fraud")
        for i, q in enumerate(fq, 1):
            print(f"      {i}. {q}")

        print("\n  [3] Summarization:")
        test_text = (
            "I was cheated via UPI payment. Someone called me pretending to be "
            "from SBI customer care and asked me to share my OTP. I shared it "
            "and Rs 50,000 was deducted from my account. I filed a complaint "
            "with cyber cell in Delhi but no action has been taken yet."
        )
        summary = summarize_complaint(test_text)
        print(f"      {summary}")

        print("\n  [4] Classification:")
        cls = classify_result(test_text, "UPI fraud")
        print(f"      {cls}")
