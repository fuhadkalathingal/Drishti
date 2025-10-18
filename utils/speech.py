from gtts import gTTS
import pygame
import tempfile
import os

def speak(text, lang='en', slow=False):
    """
    Speak the given text using gTTS and pygame.
    
    Args:
        text (str): Text to speak.
        lang (str): Language code ('en' for English, 'es' for Spanish, etc.)
        slow (bool): True for slower speech, False for normal speed.
    """
    # Create temporary file for mp3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        temp_path = fp.name

    # Convert text to speech
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save(temp_path)

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()

    # Wait until speech finishes
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Clean up temp file
    os.remove(temp_path)

# Example usage
if __name__ == '__main__':
    speak("Hello! Speaking fast using gTTS", slow=False)
    speak("Hello! Speaking slowly using gTTS.", slow=True)
