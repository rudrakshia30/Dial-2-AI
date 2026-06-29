import re

# Whisper often mis-hears "dubara bolo" as goodbye/bye — handled in transcript_fix.
from app.services.transcript_fix import is_repeat_stt_garbage
_REPEAT_PATTERNS = [
    r"\brepeat\b",
    r"\bsay\s+it\s+again\b",
    r"\bsay\s+that\s+again\b",
    r"\bsay\s+again\b",
    r"\btell\s+again\b",
    r"\bone\s+more\s+time\b",
    r"\bcan\s+you\s+repeat\b",
    r"\bplease\s+repeat\b",
    r"\btell\s+me\s+again\b",
    r"\bwhat\s+did\s+you\s+say\b",
    r"\bdobara\s+bol",
    r"\bdubara\s+bol",
    r"\bdovara\s+bol",
    r"\bdu\s+bara\s+bol",
    r"\bdo\s+bara\s+bol",
    r"\bphir\s+se\s+bol",
    r"\bfir\s+se\s+bol",
    r"\bwapas\s+bol",
    r"\bdobara\s+sunao",
    r"\bphir\s+se\s+sunao",
    r"\bdovara\s+bata",
    r"\bdubara\s+bata",
    r"\bdobara\s+bata",
    r"\brepeat\s+karo\b",
    r"\brepeat\s+kar\b",
    r"\banswer\s+repeat\b",
    r"\bjawab\s+dobara\b",
    r"\bjawab\s+phir\s+se\b",
    r"\bpehle\s+wala\s+jawab\b",
    r"\blast\s+answer\b",
    r"\bdo\s+it\s+again\b",
    r"\bdo\s+you\s+know\s+again\b",
    r"\bknow\s+again\b",
]

# Devanagari repeat phrases (e.g. "दुबारा बोलो", "फिर से बोलो").
_DEVANAGARI_REPEAT_MARKERS = (
    "दुबारा",
    "दोबारा",
    "फिर से",
    "फिरसे",
    "दोहराओ",
    "दोहराना",
    "फिर बोल",
)

# Common Whisper mis-hearings of "dubara bolo" / repeat requests.
_REPEAT_STT_MISTRANSCRIPTIONS = (
    "do you know again",
    "do it again",
    "du bara bolo",
    "do bara bolo",
    "the bara bolo",
    "dubara bolo",
    "dobara bolo",
    "dovara bolo",
    "dovara batau",
    "dovara batao",
    "dubara batau",
    "dubara batao",
    "phir se bolo",
    "fir se bolo",
    "say again",
    "tell again",
)

_REPEAT_FILLER_WORDS = frozenset(
    {
        "do", "you", "know", "can", "please", "say", "tell", "me", "it", "that",
        "again", "repeat", "one", "more", "time", "the", "a", "an", "to", "i",
        "we", "my", "your", "karo", "kar", "bol", "bolo", "sunao", "wapas",
        "dobara", "dubara", "dovara", "phir", "fir", "se", "bara", "du", "bar",
        "batau", "batao", "bata", "bataiye",
    }
)

_QUESTION_STARTS = (
    "who", "what", "when", "where", "why", "how", "which", "whom", "whose",
    "is", "are", "was", "were", "kya", "kaun", "kab", "kahan", "kyun",
    "tell", "explain", "define", "describe",
)

_TOPIC_MARKERS = (
    "net worth", "history", "weather", "price", "prime minister", "president",
    "mausam", "yojana", "scheme", "news", "killed", "worth",
)

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _REPEAT_PATTERNS]

_HINDI_MARKERS = (
    "kya", "hai", "main", "aap", "ka", "ki", "ke", "mein", "nahi", "bolo",
    "kripya", "maaf", "jawab", "sawal", "dobara", "phir", "sunao", "karo",
    "mujhe", "aapki", "aapka", "kijiye", "boliye",
)

_ENGLISH_MARKERS = (
    "the", "what", "how", "who", "whom", "whose", "which", "when", "where", "why",
    "please", "repeat", "again", "answer", "tell", "can", "you", "would", "say",
    "previous", "last", "available", "is", "are", "was", "were", "of", "in", "for",
    "prime", "minister", "president", "india",
)

_NO_ANSWER_MESSAGES = {
    "english": "I'm sorry, there is no previous answer available to repeat.",
    "hindi": "Maaf kijiye, dohrane ke liye koi pichla jawab uplabdh nahi hai.",
    "hinglish": "Sorry, repeat karne ke liye koi pehle ka answer available nahi hai.",
}


def _normalize(text: str) -> str:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _has_devanagari_repeat(text: str) -> bool:
    if not text:
        return False
    if not re.search(r"[\u0900-\u097F]", text):
        return False
    if len(text.strip()) > 80:
        return False
    return any(marker in text for marker in _DEVANAGARI_REPEAT_MARKERS)


def _looks_like_new_question(text: str) -> bool:
    if not text or not text.strip():
        return False

    if "?" in text:
        return True

    normalized = _normalize(text)
    words = normalized.split()
    if words and words[0] in _QUESTION_STARTS:
        return True

    lowered = text.lower()
    if any(topic in lowered for topic in _TOPIC_MARKERS):
        return True

    return len(words) > 8


def _is_short_repeat_heuristic(normalized: str) -> bool:
    """Catch short STT outputs like 'do you know again' with no real question content."""
    if not normalized:
        return False

    words = normalized.split()
    if len(words) > 6:
        return False

    if not any(
        token in normalized
        for token in ("again", "repeat", "dobara", "dubara", "dovara", "phir", "fir", "wapas", "batau", "batao")
    ):
        return False

    first_word = words[0]
    if first_word in _QUESTION_STARTS and len(words) > 3:
        return False

    content_words = [w for w in words if w not in _REPEAT_FILLER_WORDS]
    return len(content_words) == 0


def is_repeat_request(text: str) -> bool:
    """Return True when the user is asking to repeat the last AI answer."""
    if not text or not text.strip():
        return False

    if _has_devanagari_repeat(text):
        return True

    normalized = _normalize(text)
    if not normalized:
        return False

    for phrase in _REPEAT_STT_MISTRANSCRIPTIONS:
        if phrase in normalized:
            return True

    for pattern in _COMPILED_PATTERNS:
        if pattern.search(normalized):
            return True

    return _is_short_repeat_heuristic(normalized)


def is_probably_repeat_request(
    text: str,
    audio_duration_sec: float = 0.0,
    has_cached_answer: bool = False,
) -> bool:
    """
    Detect repeat intent even when STT garbles short phrases like 'dubara bolo'.
    """
    if is_repeat_request(text):
        return True

    if not has_cached_answer:
        return False

    if is_repeat_stt_garbage(text):
        return True

    # Short clips right after an answer are usually repeat requests.
    if audio_duration_sec and audio_duration_sec <= 4.5:
        if not text or not text.strip():
            return True
        if _has_devanagari_repeat(text):
            return True

    return False


def detect_language(text: str) -> str:
    """Rough language tag for spoken replies: english, hindi, or hinglish."""
    if not text or not text.strip():
        return "hinglish"

    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    lowered = text.lower().strip()
    words = re.findall(r"[a-zA-Z]+", lowered)

    if words:
        english_question_starts = (
            "who", "what", "when", "where", "why", "how", "which", "is", "are",
            "was", "were", "do", "does", "did", "can", "could", "will", "would",
        )
        if words[0] in english_question_starts:
            return "english"

    hindi_count = sum(1 for marker in _HINDI_MARKERS if marker in lowered)
    english_count = sum(1 for marker in _ENGLISH_MARKERS if re.search(rf"\b{re.escape(marker)}\b", lowered))

    if english_count > 0 and hindi_count == 0:
        return "english"
    if hindi_count > 0 and english_count == 0:
        return "hindi"
    if hindi_count > 0 and english_count > 0:
        return "hinglish"
    if re.search(r"[a-zA-Z]", text) and hindi_count == 0:
        return "english"
    return "hinglish"


def get_no_repeat_answer_message(language: str) -> str:
    return _NO_ANSWER_MESSAGES.get(language, _NO_ANSWER_MESSAGES["hinglish"])


def should_cache_as_successful_answer(user_text: str, reply: str, is_repeat: bool) -> bool:
    """Only cache real LLM answers, not errors, empty-input prompts, or repeat fallbacks."""
    if is_repeat or not user_text.strip() or not reply.strip():
        return False

    no_cache_replies = {
        "Maaf kijiye, mujhe aapki aawaz nahi aayi. Kripya apna sawaal bolein.",
        _NO_ANSWER_MESSAGES["english"],
        _NO_ANSWER_MESSAGES["hindi"],
        _NO_ANSWER_MESSAGES["hinglish"],
        "Maaf kijiye, thodi der mein dobara try karein.",
    }
    return reply not in no_cache_replies
