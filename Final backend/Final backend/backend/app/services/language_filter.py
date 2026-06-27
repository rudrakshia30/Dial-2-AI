import re

WHISPER_PROMPT = (
    "Hindi Hinglish English India phone call. "
    "Vocabulary: mausam, khabar, sawaal, jawab, train, ticket, recharge, mobile, "
    "bazaar, keemat, zaroorat, dikkat, matlab, yojana, dastavez, waqt, kiraya, "
    "pradhanmantri, rashtrapati, Droupadi Murmu, Narendra Modi, dubara bolo, phir se bolo, "
    "tamatar, taaza khabar, sarkari yojana, rozgaar, shukriya, safar, ilaaj."
)


_DEVANAGARI_EXPLICIT_RE = re.compile(
    r"devanagari|devnagri|देवनागरी",
    re.IGNORECASE,
)


def user_wants_devanagari(text: str) -> bool:
    return bool(_DEVANAGARI_EXPLICIT_RE.search(text or ""))


def contains_disallowed_script(text: str) -> bool:
    """Reject scripts outside Hindi (Devanagari), English (Latin), and common punctuation."""
    if not text:
        return False

    for char in text.strip():
        if char.isspace():
            continue
        if char.isdigit():
            continue
        if char in ".,!?\"'-:;()[]{}…\u2018\u2019\u0964\u0965":
            continue
        if char.isascii() and char.isalpha():
            continue
        if "\u0900" <= char <= "\u097F":
            continue
        return True
    return False


def is_allowed_transcript(text: str) -> bool:
    """True when transcript looks like Hindi, English, or Hinglish."""
    if not text or not text.strip():
        return True
    return not contains_disallowed_script(text)


def sanitize_transcript(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned
