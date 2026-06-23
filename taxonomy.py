"""
CrimeSignal-IN — taxonomy.py
Crime type taxonomy with categories, subtypes, and search keywords.
Used by query_expander to build search queries from user input.
"""

# ──────────────────────────────────────────────
# Main crime taxonomy dictionary
# ──────────────────────────────────────────────
CRIME_TAXONOMY = {
    "cyber_crime": {
        "label": "Cyber Crime",
        "subtypes": {
            "phishing": [
                "phishing", "phishing attack", "phishing email",
                "phishing link", "credential theft", "phishing SMS"
            ],
            "upi_fraud": [
                "UPI fraud", "UPI scam", "UPI payment fraud",
                "unauthorized UPI transaction", "UPI money lost",
                "Google Pay fraud", "PhonePe scam", "Paytm fraud"
            ],
            "otp_scam": [
                "OTP scam", "OTP fraud", "one time password scam",
                "OTP sharing scam", "fake OTP", "OTP forwarding scam"
            ],
            "loan_app_scam": [
                "loan app scam", "instant loan app fraud",
                "predatory loan app", "loan app harassment",
                "fake loan app", "Chinese loan app", "loan app threats"
            ],
            "investment_scam": [
                "investment scam", "investment fraud",
                "fake investment scheme", "high return scam",
                "crypto scam India", "trading scam", "stock tip fraud"
            ],
            "deepfake_abuse": [
                "deepfake abuse", "deepfake scam", "AI voice scam",
                "deepfake video fraud", "synthetic media fraud",
                "AI generated fake video"
            ],
            "sextortion": [
                "sextortion", "sextortion scam", "webcam blackmail",
                "intimate video blackmail", "sexual extortion",
                "video call blackmail"
            ],
            "fake_customer_care": [
                "fake customer care", "fake support number",
                "customer care scam", "fake helpline",
                "impersonation scam", "fake bank call"
            ],
            "instagram_fraud": [
                "Instagram fraud", "Instagram scam",
                "fake Instagram account", "Instagram money scam",
                "IG fraud", "Instagram investment scam"
            ],
            "whatsapp_fraud": [
                "WhatsApp fraud", "WhatsApp scam",
                "WhatsApp OTP scam", "WhatsApp job scam",
                "WhatsApp lottery scam", "WhatsApp video call scam"
            ],
        },
    },
    "sexual_crime": {
        "label": "Sexual Crime",
        "subtypes": {
            "sextortion": [
                "sextortion", "sextortion scam", "webcam blackmail",
                "intimate video blackmail", "sexual extortion",
                "revenge porn threat"
            ],
            "blackmail": [
                "blackmail", "blackmail threat", "extortion",
                "sexual blackmail", "photo blackmail", "video blackmail"
            ],
            "harassment": [
                "sexual harassment", "online sexual harassment",
                "cyber harassment", "unwanted sexual advances",
                "sexual messages", "eve teasing"
            ],
            "non_consensual_video": [
                "non-consensual video", "revenge porn",
                "intimate image abuse", "leaked private video",
                "video shared without consent", "MMS leaked"
            ],
        },
    },
    "financial_fraud": {
        "label": "Financial Fraud",
        "subtypes": {
            "ponzi_scheme": [
                "Ponzi scheme", "pyramid scheme",
                "multi-level marketing scam", "fake investment returns",
                "chain money scheme", "MLM fraud India"
            ],
            "fake_job": [
                "fake job offer", "job scam", "employment fraud",
                "work from home scam", "data entry job scam",
                "placement scam", "fake interview scam"
            ],
            "fake_rent": [
                "fake rent", "rental scam", "advance rent fraud",
                "fake landlord", "property rental scam", "deposit fraud"
            ],
            "insurance_fraud": [
                "insurance fraud", "fake insurance policy",
                "insurance claim scam", "policy mis-selling",
                "fraudulent insurance agent"
            ],
            "lottery_scam": [
                "lottery scam", "fake lottery", "prize scam",
                "KBC scam", "winner notification scam", "lottery fraud"
            ],
        },
    },
    "harassment": {
        "label": "Harassment",
        "subtypes": {
            "workplace_harassment": [
                "workplace harassment", "office harassment",
                "boss harassment", "colleague harassment",
                "hostile work environment", "POSH complaint"
            ],
            "online_harassment": [
                "online harassment", "cyber harassment",
                "internet harassment", "social media harassment",
                "trolling", "cyberbullying India"
            ],
            "stalking": [
                "stalking", "cyberstalking", "online stalking",
                "persistent following", "unwanted contact",
                "digital stalking"
            ],
            "caste_based_harassment": [
                "caste harassment", "caste discrimination",
                "caste based abuse", "Dalit harassment",
                "SC ST harassment", "untouchability"
            ],
        },
    },
    "abuse": {
        "label": "Abuse",
        "subtypes": {
            "domestic_abuse": [
                "domestic abuse", "domestic violence",
                "spousal abuse", "partner abuse",
                "family violence", "intimate partner violence",
                "section 498a"
            ],
            "child_abuse": [
                "child abuse", "child sexual abuse",
                "child neglect", "child exploitation",
                "minor abuse", "POCSO"
            ],
            "elder_abuse": [
                "elder abuse", "senior abuse",
                "elderly neglect", "aging parent abuse",
                "senior citizen fraud", "old age home abuse"
            ],
        },
    },
}

# ──────────────────────────────────────────────
# Complaint vocabulary markers (scoring + query expansion)
# ──────────────────────────────────────────────
COMPLAINT_VOCABULARY = [
    "cheated", "scammed", "fraud", "threatened", "blackmail",
    "lost money", "help", "complaint", "FIR", "police",
    "victim", "trap", "fake", "please help", "what should I do",
    "lost", "stolen", "hacked", "cheating", "scammer",
    "fraudster", "police complaint", "cyber cell", "legal help",
    "need help", "urgent help", "what to do", "guidance",
    "consumer court", "cybercrime portal", "report",
]

# ──────────────────────────────────────────────
# Region keywords for Indian states/cities
# ──────────────────────────────────────────────
REGION_KEYWORDS = {
    "delhi":       ["Delhi", "New Delhi", "NCR", "Noida", "Gurgaon", "Gurugram", "Faridabad", "Ghaziabad"],
    "mumbai":      ["Mumbai", "Bombay", "Navi Mumbai", "Thane", "MMR"],
    "bangalore":   ["Bangalore", "Bengaluru", "Karnataka"],
    "hyderabad":   ["Hyderabad", "Telangana", "Cyberabad"],
    "chennai":     ["Chennai", "Madras", "Tamil Nadu"],
    "kolkata":     ["Kolkata", "Calcutta", "West Bengal"],
    "pune":        ["Pune", "Maharashtra"],
    "ahmedabad":   ["Ahmedabad", "Gujarat"],
    "jaipur":      ["Jaipur", "Rajasthan"],
    "lucknow":     ["Lucknow", "Uttar Pradesh", "UP"],
    "bhopal":      ["Bhopal", "Madhya Pradesh", "MP"],
    "indore":      ["Indore", "Madhya Pradesh"],
    "chandigarh":  ["Chandigarh", "Punjab", "Haryana"],
    "kochi":       ["Kochi", "Cochin", "Kerala"],
    "bhubaneswar": ["Bhubaneswar", "Odisha", "Orissa"],
    "patna":       ["Patna", "Bihar"],
    "ranchi":      ["Ranchi", "Jharkhand"],
    "guwahati":    ["Guwahati", "Assam"],
}

# ──────────────────────────────────────────────
# Platform-specific search terms
# ──────────────────────────────────────────────
PLATFORM_KEYWORDS = [
    "Reddit", "r/india", "r/LegalAdviceIndia", "r/digitaldost",
    "Quora", "Twitter", "X.com", "Facebook", "Telegram",
    "consumerforum", "consumercomplaints.in", "pgportal",
    "YouTube comments", "Instagram", "WhatsApp",
]


# ──────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────
def get_all_subtypes() -> list[str]:
    """Return flat list of all crime subtype keys across categories."""
    subtypes = []
    for category in CRIME_TAXONOMY.values():
        subtypes.extend(category["subtypes"].keys())
    return subtypes


def get_subtype_keywords(subtype_name: str) -> list[str]:
    """Get search keywords for a specific subtype."""
    for category in CRIME_TAXONOMY.values():
        if subtype_name in category["subtypes"]:
            return category["subtypes"][subtype_name]
    return []


def get_category_keywords(category_key: str) -> list[str]:
    """Get ALL keywords across every subtype in a category."""
    cat = CRIME_TAXONOMY.get(category_key)
    if not cat:
        return []
    keywords = []
    for kw_list in cat["subtypes"].values():
        keywords.extend(kw_list)
    return keywords


def get_category_for_subtype(subtype_name: str) -> str:
    """Find which category a subtype belongs to."""
    for cat_key, category in CRIME_TAXONOMY.items():
        if subtype_name in category["subtypes"]:
            return cat_key
    return ""


def get_region_keywords(region: str) -> list[str]:
    """Get region-specific keywords for search."""
    region_lower = region.strip().lower()
    return REGION_KEYWORDS.get(region_lower, [region])


def resolve_crime_input(user_input: str) -> dict:
    """
    Resolve free-text crime input to taxonomy entries.
    Returns {"category": str, "subtypes": [str], "keywords": [str]}
    """
    user_lower = user_input.strip().lower().replace(" ", "_")

    # Direct category match
    if user_lower in CRIME_TAXONOMY:
        return {
            "category": user_lower,
            "subtypes": list(CRIME_TAXONOMY[user_lower]["subtypes"].keys()),
            "keywords": get_category_keywords(user_lower),
        }

    # Direct subtype match
    for cat_key, cat in CRIME_TAXONOMY.items():
        if user_lower in cat["subtypes"]:
            return {
                "category": cat_key,
                "subtypes": [user_lower],
                "keywords": cat["subtypes"][user_lower],
            }

    # Fuzzy: check if user input appears in any keyword list
    user_words = user_input.strip().lower()
    for cat_key, cat in CRIME_TAXONOMY.items():
        for sub_key, kw_list in cat["subtypes"].items():
            for kw in kw_list:
                if user_words in kw.lower() or kw.lower() in user_words:
                    return {
                        "category": cat_key,
                        "subtypes": [sub_key],
                        "keywords": kw_list,
                    }

    # Fallback — return user input as-is
    return {
        "category": "unknown",
        "subtypes": [],
        "keywords": [user_input],
    }
