import re


# Whisper often mis-hears "dubara bolo" as goodbye/bye.
_REPEAT_STT_GARBAGE = frozenset(
    {
        "goodbye",
        "good bye",
        "good by",
        "bye",
        "bye bye",
        "by bye",
        "by by",
        "good-bye",
    }
)

# Wrong Devanagari forms -> correct form.
_DEVANAGARI_FIXES = (
    ("प्रदान मुंत्री", "प्रधानमंत्री"),
    ("प्रदान मंत्री", "प्रधानमंत्री"),
    ("प्रदानमंत्री", "प्रधानमंत्री"),
    ("तरदान मंतरी", "प्रधानमंत्री"),
    ("तरदान मंत्री", "प्रधानमंत्री"),
    ("तरदानमंत्री", "प्रधानमंत्री"),
    ("प्रधान मंत्री", "प्रधानमंत्री"),
    ("प्रधानमन्त्री", "प्रधानमंत्री"),
    ("राश्ट्रपती", "राष्ट्रपति"),
    ("राष्ट्रपती", "राष्ट्रपति"),
    ("राश्त्रपति", "राष्ट्रपति"),
    ("ग्यानाम", "नाम"),
    ("नामा है", "नाम है"),
    ("नामा", "नाम"),
    ("कौन nama", "कौन"),
)

_ROMAN_FIXES = (
    (re.compile(r"\bprad?an\s*mu?n?tri\b", re.I), "pradhan mantri"),
    (re.compile(r"\btaradan\s*mant?ri\b", re.I), "pradhan mantri"),
    (re.compile(r"\bpradhanmantri\b", re.I), "pradhan mantri"),
    (re.compile(r"\bgyanam\b", re.I), "naam"),
    (re.compile(r"\brashtrapati\b", re.I), "rashtrapati"),
    (re.compile(r"\brash?trapati\b", re.I), "rashtrapati"),
    (re.compile(r"\bma?s?tr[a]?\s*pat[iy]\b", re.I), "rashtrapati"),
    (re.compile(r"\bkorn\b", re.I), "kaun"),
    (re.compile(r"\bkoun\b", re.I), "kaun"),
    (re.compile(r"\bkon\b", re.I), "kaun"),
)


def is_repeat_stt_garbage(text: str) -> bool:
    normalized = re.sub(r"[^\w\s]", " ", (text or "").lower()).strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized in _REPEAT_STT_GARBAGE


def get_repeat_user_log_text(raw_stt: str = "") -> str:
    """Stable transcript label for repeat turns (STT often garbles short phrases)."""
    if raw_stt and is_repeat_stt_garbage(raw_stt):
        return "dubara bolo (repeat request)"
    if raw_stt and raw_stt.strip():
        cleaned = raw_stt.strip()
        if len(cleaned) <= 40:
            return f"{cleaned} (repeat request)"
    return "dubara bolo (repeat request)"


def normalize_user_transcript(text: str) -> str:
    """Fix common Hindi STT errors before LLM or repeat detection."""
    if not text or not text.strip():
        return text

    corrected = text.strip()
    corrected = re.sub(r"\s+", " ", corrected)

    for wrong, right in _DEVANAGARI_FIXES:
        corrected = corrected.replace(wrong, right)

    for pattern, replacement in _ROMAN_FIXES:
        corrected = pattern.sub(replacement, corrected)

    if corrected != text.strip():
        print(f"STT corrected: '{text}' -> '{corrected}'")

    return corrected
