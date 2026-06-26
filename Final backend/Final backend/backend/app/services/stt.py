import os

import httpx
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

XAI_STT_URL = "https://api.groq.com/openai/v1/stt"


def _xai_stt_headers():
    return {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY  ')}"}


def transcribe_wav(wav_path):
    try:
        with open(wav_path, "rb") as f:
            response = httpx.post(
                XAI_STT_URL,
                headers=_xai_stt_headers(),
                files={"file": ("audio.wav", f, "audio/wav")},
                timeout=60.0,
            )
        response.raise_for_status()
        text = response.json().get("text", "").strip()
        print(f"Grok STT: '{text}'")
        return text
    except Exception as e:
        print("Grok STT ERROR:", repr(e))
        # Fallback to speech_recognition
        try:
            r = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio = r.record(source)
            return r.recognize_google(
                audio,
                language="hi-IN"
            )
        except Exception as se:
            print("Fallback STT ERROR:", repr(se))
            return ""


async def transcribe_audio(audio_url):
    if not audio_url:
        return ""
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                XAI_STT_URL,
                headers=_xai_stt_headers(),
                data={"url": audio_url},
                timeout=60.0,
            )
            if response.status_code != 200:
                print(f"Grok STT failed: status {response.status_code}")
                return ""
            text = response.json().get("text", "").strip()
            print(f"Grok URL STT: '{text}'")
            return text
    except Exception as e:
        print("Grok URL STT ERROR:", repr(e))
        return ""
