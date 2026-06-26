import os
import shutil
import subprocess


def _resolve_ffmpeg() -> str:
    """Return an ffmpeg executable path (bundled imageio-ffmpeg or system PATH)."""
    try:
        import imageio_ffmpeg

        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and os.path.isfile(bundled):
            return bundled
    except Exception:
        pass

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    raise FileNotFoundError(
        "ffmpeg not found. Install ffmpeg and add it to PATH, or run: pip install imageio-ffmpeg"
    )


def mp3_to_pcm(mp3_file, pcm_file, sample_rate=8000):
    if not os.path.isfile(mp3_file):
        raise FileNotFoundError(f"MP3 input not found: {mp3_file}")

    os.makedirs(os.path.dirname(os.path.abspath(pcm_file)) or ".", exist_ok=True)
    ffmpeg = _resolve_ffmpeg()

    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            mp3_file,
            "-f",
            "s16le",
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            pcm_file,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    if not os.path.isfile(pcm_file):
        raise FileNotFoundError(f"PCM output was not created: {pcm_file}")

    return pcm_file
