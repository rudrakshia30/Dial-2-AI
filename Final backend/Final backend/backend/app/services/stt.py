import os

import httpx
import speech_recognition as sr
from dotenv import load_dotenv

from app.services.language_filter import (
    WHISPER_PROMPT,
    is_allowed_transcript,
    sanitize_transcript,
)

load_dotenv()

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_STT_MODEL = "whisper-large-v3-turbo"


def _groq_api_key() -> str:
    key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not key:
        raise ValueError("GROQ_API_KEY not found in environment")
    return key


def _groq_stt_headers():
    return {"Authorization": f"Bearer {_groq_api_key()}"}


def _groq_transcribe(wav_path: str, language: str | None = None) -> str:
    data = {
        "model": GROQ_STT_MODEL,
        "response_format": "json",
        "prompt": WHISPER_PROMPT,
    }
    if language:
        data["language"] = language

    with open(wav_path, "rb") as f:
        response = httpx.post(
            GROQ_STT_URL,
            headers=_groq_stt_headers(),
            files={"file": ("audio.wav", f, "audio/wav")},
            data=data,
            timeout=60.0,
        )
    response.raise_for_status()
    return sanitize_transcript(response.json().get("text", ""))


def _google_transcribe(wav_path: str, language: str = "hi-IN") -> str:
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    return sanitize_transcript(
        r.recognize_google(audio, language=language)
    )


def transcribe_wav(wav_path):
    attempts = [
        ("auto", None),
        ("hi", "hi"),
        ("en", "en"),
    ]
    last_text = ""

    for label, lang in attempts:
        try:
            text = _groq_transcribe(wav_path, language=lang)
            last_text = text
            if text and is_allowed_transcript(text):
                print(f"Groq STT ({label}): '{text}'")
                return text
            if text:
                print(f"Groq STT ({label}) rejected disallowed script: '{text}'")
        except Exception as e:
            print(f"Groq STT ({label}) ERROR:", repr(e))

    for language in ("hi-IN", "en-IN"):
        try:
            text = _google_transcribe(wav_path, language=language)
            last_text = text
            if text and is_allowed_transcript(text):
                print(f"Fallback STT ({language}): '{text}'")
                return text
            if text:
                print(f"Fallback STT ({language}) rejected disallowed script: '{text}'")
        except Exception as se:
            print(f"Fallback STT ({language}) ERROR:", repr(se))

    if last_text and not is_allowed_transcript(last_text):
        print("STT: all attempts returned disallowed language/script — treating as empty.")
        return ""

    return last_text if is_allowed_transcript(last_text) else ""


async def transcribe_audio(audio_url):
    if not audio_url:
        return ""
    try:
        async with httpx.AsyncClient() as http_client:
            audio_response = await http_client.get(audio_url, timeout=60.0)
            audio_response.raise_for_status()
            response = await http_client.post(
                GROQ_STT_URL,
                headers=_groq_stt_headers(),
                files={"file": ("audio.wav", audio_response.content, "audio/wav")},
                data={
                    "model": GROQ_STT_MODEL,
                    "response_format": "json",
                    "prompt": WHISPER_PROMPT,
                },
                timeout=60.0,
            )
            if response.status_code != 200:
                print(f"Groq STT failed: status {response.status_code}")
                return ""
            text = sanitize_transcript(response.json().get("text", ""))
            if text and not is_allowed_transcript(text):
                print(f"Groq URL STT rejected disallowed script: '{text}'")
                return ""
            print(f"Groq URL STT: '{text}'")
            return text
    except Exception as e:
        print("Groq URL STT ERROR:", repr(e))
        return ""
