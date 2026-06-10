from gtts import gTTS


def text_to_speech(text, output_file="reply.mp3"):

    tts = gTTS(
        text=text,
        lang="hi"
    )

    tts.save(output_file)

    return output_file