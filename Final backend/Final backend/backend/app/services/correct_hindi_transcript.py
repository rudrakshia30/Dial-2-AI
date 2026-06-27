"""
Hindi/Hinglish transcript correction pipeline.

Flow: raw STT -> rule-based fixes -> optional Groq contextual correction -> corrected query
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.services.llm import MODEL, _get_client
from app.services.repeat_intent import detect_language, is_repeat_request
from app.services.transcript_fix import normalize_user_transcript

# Commonly used Hindi/Hinglish vocabulary (Urdu/Persian/Arabic/Punjabi/Gujarati/English origin).
_EVERYDAY_LOANWORD_HINTS = (
    "zaroorat", "dikkat", "matlab", "sawaal", "sawal", "jawab", "khabar", "mausam",
    "ilaaj", "daftar", "tareekh", "waqt", "hisaab", "keemat", "bazaar", "safar",
    "madad", "faisla", "mumkin", "shukriya", "rozgaar", "zameen", "dukaan", "kiraya",
    "mobile", "recharge", "train", "ticket", "dastavez", "dastavaez", "yojana",
    "tamatar", "taaza", "sarkari", "batao", "bataiye", "chahiye",
)

_ENGLISH_QUESTION_STARTS = (
    "who", "what", "when", "where", "why", "how", "which", "is", "are", "was",
    "were", "do", "does", "did", "can", "could", "will", "would", "tell", "give",
)

_HINDI_ROMAN_MARKERS = (
    "kya", "hai", "hain", "ka", "ki", "ke", "ko", "mein", "main", "mujhe", "aap",
    "apka", "apke", "kripya", "batao", "bataiye", "kaun", "kab", "kahan", "kyun",
    "nahi", "nahin", "chahiye", "karna", "hoga", "rahega", "wala", "wali", "wale",
)

_GARBLE_MARKERS = (
    "प्रदान", "तरदान", "राश्ट्रपती", "ग्यानाम", "नामा", "munta", "taradan", "pradan",
    "gyanam", "mantra", "mastr pati", "mastra pati", "korn",
)

CORRECTION_SYSTEM_PROMPT = """You fix garbled Hindi/Hinglish/English phone-call speech-to-text transcripts.

Return ONLY valid JSON with keys:
- corrected: string (reconstructed user question/intent in natural Roman Hindi, Hinglish, or English matching the speaker's language; never translate Hindi to English unless the speaker clearly spoke English)
- language: one of english, hindi, hinglish
- needs_clarification: boolean
- clarification: string (one short clarification question in the same language if needs_clarification is true, else empty)

Rules:
- Fix phonetic STT mistakes using full sentence and conversation context.
- Understand Urdu/Persian/Arabic/Punjabi/Gujarati/English loanwords used in everyday Hindi (zaroorat, dikkat, mausam, khabar, train, ticket, recharge, bazaar, keemat, dastavez, etc.).
- Preserve names, numbers, dates, prices, locations, phone numbers unless context makes a correction highly certain.
- Do not invent facts or add details the user did not imply.
- Do not overcorrect if the transcript already makes sense.
- Use conversation history to resolve ambiguous phrases (e.g. train timing questions).
- "Mastra Pati korn hai" or similar garble usually means "Bharat ke rashtrapati kaun hain".
- "Pradhan mantri" / "rashtrapati" India office questions must be reconstructed clearly.
- For repeat requests (dubara bolo, phir se, repeat), return the corrected repeat phrase clearly.
- Output Roman script for Hindi/Hinglish unless the user explicitly asked for Devanagari."""


@dataclass
class TranscriptCorrectionResult:
    raw_transcript: str
    corrected_transcript: str
    detected_language: str
    used_llm: bool = False
    needs_clarification: bool = False
    clarification_question: str = ""


def detect_input_language(text: str) -> str:
    """
    Detect english, hindi, or hinglish.
    Hindi includes Devanagari and Roman Hindi with everyday Urdu/Persian/English loanwords.
    """
    if not text or not text.strip():
        return "hinglish"

    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    lowered = text.lower()
    words = re.findall(r"[a-zA-Z]+", lowered)

    english_hits = sum(
        1 for w in words
        if w in _ENGLISH_QUESTION_STARTS or (len(w) > 4 and w.isascii())
    )
    hindi_hits = sum(
        1 for m in _HINDI_ROMAN_MARKERS
        if re.search(rf"\b{re.escape(m)}\b", lowered)
    )
    loan_hits = sum(1 for m in _EVERYDAY_LOANWORD_HINTS if m in lowered)

    if words and words[0] in _ENGLISH_QUESTION_STARTS and hindi_hits == 0:
        return "english"

    if hindi_hits > 0 and english_hits > 0:
        return "hinglish"
    if hindi_hits > 0 or loan_hits >= 2:
        return "hindi" if english_hits == 0 else "hinglish"
    if english_hits > 0 and hindi_hits == 0 and loan_hits == 0:
        return "english"

    return detect_language(text)


def _has_garble_indicators(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(marker in text or marker in lowered for marker in _GARBLE_MARKERS)


def _looks_clean_english(text: str) -> bool:
    if not text.strip():
        return False
    if re.search(r"[\u0900-\u097F]", text):
        return False
    lang = detect_input_language(text)
    if lang != "english":
        return False
    return not _has_garble_indicators(text)


def _looks_clean_hindi_or_hinglish(text: str) -> bool:
    if not text.strip():
        return False
    if _has_garble_indicators(text):
        return False
    lang = detect_input_language(text)
    if lang == "english":
        return False
    if len(text.split()) >= 3 and not re.search(r"[A-Za-z]{15,}", text):
        return True
    return False


def _needs_llm_correction(raw: str, rule_corrected: str, language: str) -> bool:
    if not rule_corrected.strip():
        return False
    if is_repeat_request(raw) or is_repeat_request(rule_corrected):
        return False
    if language == "english" and _looks_clean_english(rule_corrected):
        return False
    if _looks_clean_hindi_or_hinglish(rule_corrected) and rule_corrected.strip() == raw.strip():
        return False
    if _has_garble_indicators(raw) or _has_garble_indicators(rule_corrected):
        return True
    if rule_corrected.strip() != raw.strip():
        return True
    if language in ("hindi", "hinglish") and re.search(r"[\u0900-\u097F]", raw):
        return True
    return language in ("hindi", "hinglish") and not _looks_clean_hindi_or_hinglish(rule_corrected)


def _format_history(history: list[dict[str, Any]] | None) -> str:
    if not history:
        return "(no prior conversation)"
    lines = []
    for msg in history[-6:]:
        role = msg.get("role", "user").upper()
        content = msg.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _parse_correction_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return json.loads(cleaned)


async def _llm_correct_transcript(
    rule_corrected: str,
    raw_transcript: str,
    conversation_history: list[dict[str, Any]] | None,
    language: str,
) -> TranscriptCorrectionResult:
    history_text = _format_history(conversation_history)
    user_prompt = f"""Conversation history:
{history_text}

Raw STT transcript:
{raw_transcript}

Rule-based pre-correction:
{rule_corrected}

Detected language hint: {language}

Reconstruct the most likely intended user question."""

    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": CORRECTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=180,
        temperature=0.1,
    )
    payload = _parse_correction_json(response.choices[0].message.content.strip())
    corrected = (payload.get("corrected") or rule_corrected).strip()
    detected = payload.get("language") or language
    if detected not in ("english", "hindi", "hinglish"):
        detected = language
    needs_clarification = bool(payload.get("needs_clarification"))
    clarification = (payload.get("clarification") or "").strip()
    return TranscriptCorrectionResult(
        raw_transcript=raw_transcript,
        corrected_transcript=corrected or rule_corrected,
        detected_language=detected,
        used_llm=True,
        needs_clarification=needs_clarification,
        clarification_question=clarification,
    )


async def correct_hindi_transcript(
    raw_transcript: str,
    conversation_history: list[dict[str, Any]] | None = None,
) -> TranscriptCorrectionResult:
    """
    Correct Hindi/Hinglish STT output using rules + optional Groq contextual pass.
    Falls back to rule-based output if LLM correction fails.
    """
    raw = (raw_transcript or "").strip()
    if not raw:
        return TranscriptCorrectionResult(
            raw_transcript="",
            corrected_transcript="",
            detected_language="hinglish",
        )

    try:
        rule_corrected = normalize_user_transcript(raw)
    except Exception as exc:
        print(f"Rule-based transcript correction error: {exc}")
        rule_corrected = raw

    language = detect_input_language(rule_corrected or raw)

    if not _needs_llm_correction(raw, rule_corrected, language):
        return TranscriptCorrectionResult(
            raw_transcript=raw,
            corrected_transcript=rule_corrected or raw,
            detected_language=language,
            used_llm=False,
        )

    try:
        return await _llm_correct_transcript(
            rule_corrected=rule_corrected or raw,
            raw_transcript=raw,
            conversation_history=conversation_history,
            language=language,
        )
    except Exception as exc:
        print(f"LLM transcript correction failed, using rule-based fallback: {exc}")
        return TranscriptCorrectionResult(
            raw_transcript=raw,
            corrected_transcript=rule_corrected or raw,
            detected_language=language,
            used_llm=False,
        )
