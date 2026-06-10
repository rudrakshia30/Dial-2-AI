import speech_recognition as sr
import httpx
from app.services.llm import client
from google.genai import types

def transcribe_wav(wav_path):
    try:
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/wav"
                ),
                "Transcribe this audio call recording. Return only the transcription, in the original language (Hindi/English/Hinglish) spoken. Do not include any other text."
            ]
        )
        text = response.text.strip()
        print(f"Gemini STT: '{text}'")
        return text
    except Exception as e:
        print("Gemini STT ERROR:", repr(e))
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
        # Download audio from URL
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(audio_url, timeout=30.0)
            if response.status_code != 200:
                print(f"Failed to download audio: status {response.status_code}")
                return ""
            audio_bytes = response.content

        # Determine MIME type based on URL or defaults to wav
        mime_type = "audio/wav"
        if "mp3" in audio_url.lower():
            mime_type = "audio/mp3"

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime_type
                ),
                "Transcribe this audio call recording. Return only the transcription, in the original language (Hindi/English/Hinglish) spoken. Do not include any other text."
            ]
        )
        text = response.text.strip()
        print(f"Gemini URL STT: '{text}'")
        return text
    except Exception as e:
        print("Gemini URL STT ERROR:", repr(e))
        return ""