import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from dotenv import load_dotenv
load_dotenv()

from core.brain import think
from agents.voice_agent import speak, listen
from agents.alarm import set_speak_fn

set_speak_fn(speak)

speak("ARIA online.")

# Words that indicate ARIA is hearing itself
ARIA_OWN_WORDS = ["timer is done", "aria online", "shutting down", "goodbye", "timer set"]

while True:
    try:
        user_input = listen(duration=7)
        if not user_input or len(user_input.strip()) < 3:
            continue
        if len(user_input.split()) < 2:
            continue
        # Skip if ARIA is hearing its own output
        if any(phrase in user_input.lower() for phrase in ARIA_OWN_WORDS):
            continue
        print(f"You: {user_input}")
        if any(word in user_input.lower() for word in ["bye", "goodbye", "stop aria", "shut down"]):
            speak("Goodbye.")
            break
        response = think(user_input)
        speak(response)
    except KeyboardInterrupt:
        speak("Shutting down.")
        break
    except Exception as e:
        print(f"Error: {e}")
        continue