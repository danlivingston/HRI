import speech_recognition as sr


class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen_for_start(self, speaker):
        print("Waiting for the 'start' command. Please say 'start' to begin.")

        while True:
            with sr.Microphone() as source:
                speaker.speak("Say 'start' to begin.")
                try:
                    audio = self.recognizer.listen(source)
                    recognized_text = self.recognizer.recognize_google(audio)
                    speaker.speak(f"I think you said: {recognized_text}")

                    if recognized_text.lower() == "start":
                        speaker.speak("I understand, game is started")
                        return True
                    else:
                        speaker.speak(
                            "I did not understand you. Please repeat yourself."
                        )

                except sr.UnknownValueError:
                    print(
                        "Google Speech Recognition could not understand audio. Please try again."
                    )
                except sr.RequestError as e:
                    print(
                        f"Could not request results from Google Speech Recognition service; {e}"
                    )

    def listen_for_help(self, speaker):
        with sr.Microphone() as source:
            speaker.speak("I am listening")
            try:
                audio = self.recognizer.listen(source)
                recognized_text = self.recognizer.recognize_google(audio)
                speaker.speak(f"I think you said: {recognized_text}")

                if recognized_text.lower() == "help":
                    print("Command recognized: 'help'")
                    return True
                else:
                    speaker.speak("I did not understand you. Please repeat yourself")

            except sr.UnknownValueError:
                print(
                    "Google Speech Recognition could not understand audio. Please try again."
                )
            except sr.RequestError as e:
                print(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )
