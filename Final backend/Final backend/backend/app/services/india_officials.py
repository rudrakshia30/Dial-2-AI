"""Detection and verified facts for common India official questions."""
import re

PM_FACT = (
    "The current Prime Minister of India is Narendra Modi."
)
PRESIDENT_FACT = (
    "The current President of India is Droupadi Murmu."
)

_INDIA_MARKERS = ("भारत", "bharat", "india", "भारत के", "bharat ke")

_PM_MARKERS = (
    "प्रधानमंत्री", "प्रदान", "तरदान", "pradhan", "pradan", "taradan",
    "mantri", "munta", "mantra", "prime minister", "pradhanmantri",
)

_PRESIDENT_MARKERS = (
    "राष्ट्रपति", "राश्ट्रपति", "राश्ट्रपती", "rashtrapati", "rashtrapati",
    "rashtrpat", "rashtrapati", "president of india", "president",
)

# Phonetic STT mis-hearings of "rashtrapati kaun hai"
_PHONETIC_PRESIDENT_RES = (
    re.compile(r"ma?s?tr[a]?\s*pat[iy]", re.I),
    re.compile(r"ma?s?tr[a]?\s*patt[iy]", re.I),
    re.compile(r"rashtr\w*\s*pat[iy]", re.I),
    re.compile(r"rash?tra\s*pat[iy]", re.I),
    re.compile(r"ra[shz]tr\w*\s*pat", re.I),
)

_HISTORICAL_MARKERS = (
    "first", "1st", "second", "2nd", "third", "3rd", "previous", "former", "past", "history", "list of", "list",
    "pehle", "pehla", "pahla", "pahle", "pehli", "pahli", "purv", "pichle", "pichla", "purva", "bhootpurv", "bhootpoorv", 
    "itihaas", "itihas", "soochi", "suchi", "pehle wale", "pahle wale",
    "पहले", "पहला", "पहली", "पूर्व", "पिछले", "पिछला", "भूतपूर्व", "इतिहास", "सूची"
)


def mentions_india(text: str) -> bool:
    lowered = (text or "").lower()
    return any(m in text or m in lowered for m in _INDIA_MARKERS)


def is_historical_question(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    if any(m in lowered for m in _HISTORICAL_MARKERS):
        return True
    # Check for past years (e.g. 1950, 1999, 2015, 2021)
    if re.search(r"\b(19\d{2}|20[01]\d|202[01])\b", lowered):
        return True
    return False


def is_phonetic_president_question(text: str) -> bool:
    """Detect heavily garbled STT like 'Mastra Pati korn hai'."""
    if not text or not text.strip():
        return False
    lowered = text.lower()
    for pattern in _PHONETIC_PRESIDENT_RES:
        if pattern.search(lowered):
            return True
    if ("pati" in lowered or "patti" in lowered) and (
        "korn" in lowered or "kaun" in lowered or "koun" in lowered or "kon" in lowered
    ):
        if re.search(r"ma?s?t?r", lowered) or "rash" in lowered or "rasht" in lowered:
            return True
    return False


def is_president_question(text: str) -> bool:
    if not text or not text.strip():
        return False
    if is_historical_question(text):
        return False
    lowered = text.lower()
    if any(m in text or m in lowered for m in _PRESIDENT_MARKERS):
        if mentions_india(text) or "bharat" in lowered or "india" in lowered:
            return True
        if "kaun" in lowered or "koun" in lowered or "korn" in lowered or "kon" in lowered:
            return True
        if re.search(r"[\u0900-\u097F]", text):
            return True
    if is_phonetic_president_question(text):
        return True
    if re.search(r"president\s+of\s+india", lowered):
        return True
    return False


def is_pm_question(text: str) -> bool:
    if not text or not text.strip():
        return False
    if is_president_question(text) or is_historical_question(text):
        return False
    lowered = text.lower()
    if mentions_india(text) and any(
        m in text or m in lowered for m in _PM_MARKERS
    ):
        return True
    if re.search(r"prime\s+minister", lowered) and mentions_india(text):
        return True
    return False


def detect_india_official(text: str) -> str | None:
    if is_president_question(text):
        return "president"
    if is_pm_question(text):
        return "pm"
    return None


def normalize_india_official_question(text: str) -> str | None:
    """Return canonical Roman question if this is a PM/President query."""
    official = detect_india_official(text)
    if official == "president":
        return "Bharat ke rashtrapati kaun hain?"
    if official == "pm":
        return "Bharat ke pradhan mantri kaun hain?"
    return None


def get_official_fact_context(text: str) -> str:
    official = detect_india_official(text)
    if official == "president":
        return f"\n[FACT: {PRESIDENT_FACT}]"
    if official == "pm":
        return f"\n[FACT: {PM_FACT}]"
    return ""
