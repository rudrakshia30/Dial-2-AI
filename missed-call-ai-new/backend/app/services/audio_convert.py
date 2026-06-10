import subprocess


def mp3_to_pcm(mp3_file, pcm_file, sample_rate=8000):

    subprocess.run(
        [
            "ffmpeg",
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
            pcm_file
        ],
        check=True
    )

    return pcm_file