from io import BytesIO
import pygame
from groq import Groq
from dotenv import load_dotenv
import os

# =============================
# LOAD ENVIRONMENT VARIABLES
# =============================
load_dotenv()  # Load .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not found in environment variables or .env file!")

client = Groq(api_key=GROQ_API_KEY)

# =============================
# SPEAK FUNCTION
# =============================
def speak(text: str, voice: str = "Jennifer-PlayAI"):
    """
    Generate speech using Groq TTS and play it immediately.
    Non-blocking for other code execution.
    """
    if not text.strip():
        return

    try:
        # Generate speech
        response = client.audio.speech.create(
            model="playai-tts",
            voice=voice,
            response_format="wav",
            input=text,
        )

        # Load bytes into memory
        audio_bytes = BytesIO(response.read())  # read() gets the bytes

        # Initialize pygame mixer
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Load audio from bytes and play
        pygame.mixer.music.load(audio_bytes)
        pygame.mixer.music.play()

        # Wait until finished
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(50)

    except Exception as e:
        print(f"[Speech] Error: {e}")
    finally:
        pygame.mixer.quit()


# =============================
# TEST
# =============================
if __name__ == "__main__":
    speak("Hello! This is Drishti AI speaking.")
    speak("This is another sentence.")
