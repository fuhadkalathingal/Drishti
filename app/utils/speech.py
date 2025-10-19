from gtts import gTTS
import pygame
import time
import os

SPEECH_FILE = "temp_speech.mp3"

def speak(text, lang='en', slow=False):
    """
    Speak text using gTTS + pygame.
    This version is blocking: the program waits until the audio finishes.
    Fully cross-platform (Windows + Linux).
    """

    if not text:
        return

    # 1. Generate MP3
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(SPEECH_FILE)

    # 2. Small wait to ensure file is fully written (Linux safety)
    time.sleep(0.1)

    # 3. Stop and quit mixer in case previous playback exists
    try:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass

    # 4. Initialize mixer and play
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(SPEECH_FILE)
        pygame.mixer.music.play()

        # Wait until playback finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    finally:
        pygame.mixer.quit()

# Example usage
if __name__ == "__main__":
    speak("Hello! Speaking normally.", slow=False)
    speak("Now speaking slowly.", slow=True)
    print("Finished both speeches.")
