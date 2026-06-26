import re

# Hindi (Devanagari), English/Latin (Roman Hinglish), digits, common punctuation.
_ALLOWED_CHAR_RE = re.compile(
    r"^[\u0900-\u097Fa-zA-Z0-9\s\.,!?\"'\-:;()\u2018\u2019\u0964\u0965]+$",
    re.UNICODE,
)

# Scripts we must reject (Urdu/Arabic/Persian, etc.).
_DISALLOWED_SCRIPT_RES = (
    re.compile(r"[\u0600-\u06FF]"),  # Arabic
    re.compile(r"[\u0750-\u077F]"),  # Arabic supplement
    re.compile(r"[\u08A0-\u08FF]"),  # Arabic extended-A
    re.compile(r"[\uFB50-\uFDFF]"),  # Arabic presentation forms-A
    re.compile(r"[\uFE70-\uFEFF]"),  # Arabic presentation forms-B
)

WHISPER_PROMPT = (
    "Hindi, English, or Hinglish phone call. Roman or Devanagari script only."
)


def contains_disallowed_script(text: str) -> bool:
    if not text:
        return False
    for pattern in _DISALLOWED_SCRIPT_RES:
        if pattern.search(text):
            return True
    return False


def is_allowed_transcript(text: str) -> bool:
    """True when transcript looks like Hindi, English, or Hinglish."""
    if not text or not text.strip():
        return True
    if contains_disallowed_script(text):
        return False
    return bool(_ALLOWED_CHAR_RE.match(text.strip()))


def sanitize_transcript(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned
