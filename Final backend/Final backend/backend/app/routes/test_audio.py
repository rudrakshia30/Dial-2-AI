import wave

raw_file = r"C:\Users\HP\Desktop\missed-call-ai\backend\call_audio.raw"
wav_file = r"C:\Users\HP\Desktop\missed-call-ai\backend\call_audio.wav"

with open(raw_file, "rb") as f:
    raw_data = f.read()

with wave.open(wav_file, "wb") as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(8000)
    wav.writeframes(raw_data)

print("WAV saved:", wav_file)