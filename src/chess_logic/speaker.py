import io
import time
import os
from gtts import gTTS
import pygame


class Speaker:
    language = "en"
    tld = "com"
    slow = False

    @staticmethod
    def speak(text):
        # Generate speech
        tts = gTTS(text=text, lang=Speaker.language, tld=Speaker.tld, slow=Speaker.slow)

        # Save to a BytesIO stream instead of a file
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load the audio stream into pygame
        pygame.mixer.music.load(audio_stream, "mp3")

        # Play the audio
        pygame.mixer.music.play()

        # Wait until the audio is finished
        while pygame.mixer.music.get_busy():
            time.sleep(1)
