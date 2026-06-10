import wave


def raw_to_wav(raw_path, wav_path, sample_rate=8000):
    with open(raw_path, "rb") as f:
        raw_data = f.read()

    with wave.open(wav_path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(raw_data)

    return wav_path

def contains_speech(audio_data: bytes, threshold: int = 800) -> bool:
    """
    Checks if a chunk of 16-bit PCM audio contains actual speech by comparing
    amplitude against a threshold to ignore Exotel telecom line static.
    """
    import struct
    try:
        samples = struct.unpack(f"<{len(audio_data) // 2}h", audio_data)
        max_amplitude = max(abs(s) for s in samples)
        return max_amplitude > threshold
    except Exception:
        return True  # Fallback to true if packing fails