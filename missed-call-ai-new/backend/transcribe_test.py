import speech_recognition as sr

audio_file = r"C:\Users\HP\Desktop\missed-call-ai\backend\call_audio.wav"

r = sr.Recognizer()

with sr.AudioFile(audio_file) as source:
    audio = r.record(source)

try:
    text = r.recognize_google(audio, language="hi-IN")
    print("TEXT:", text)

except Exception as e:
    print("ERROR:", e)