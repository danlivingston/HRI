import pygame
from gtts import gTTS
import os
import time


class Speaker:
    language = "en"
    tld = "us"
    slow = False
    filename = "output.mp3"
    pygame.mixer.init()

    @staticmethod
    def speak(text):
        # Sprachdatei erzeugen
        tts = gTTS(text=text, lang=Speaker.language, tld=Speaker.tld, slow=Speaker.slow, )
        tts.save(Speaker.filename)

        # Datei laden
        pygame.mixer.music.load(Speaker.filename)

        # Datei abspielen
        pygame.mixer.music.play()

        # Warte, bis das Audio zu Ende ist
        while pygame.mixer.music.get_busy():
            time.sleep(1)

        # Lösche die Datei nach dem Abspielen
        os.remove(Speaker.filename)
