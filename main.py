import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from core.brain import think
from agents.voice_agent import speak, listen

speak("ARIA online.")

while True:
    try:
        user_input = listen(duration=5)
        if not user_input or len(user_input.strip()) < 3:
            continue
        # Skip if it sounds like noise or gibberish
        if len(user_input.split()) < 2:
            continue
        print(f"You: {user_input}")
        if any(word in user_input.lower() for word in ["bye", "goodbye", "stop aria"]):
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