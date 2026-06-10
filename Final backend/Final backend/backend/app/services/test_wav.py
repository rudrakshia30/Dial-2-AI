# test_wav.py

import speech_recognition as sr

r = sr.Recognizer()

with sr.AudioFile("call_audio.wav") as source:
    audio = r.record(source)

print("Trying English...")
try:
    print(r.recognize_google(audio))
except Exception as e:
    print("EN:", e)

print("Trying Hindi...")
try:
    print(r.recognize_google(audio, language="hi-IN"))
except Exception as e:
    print("HI:", e)