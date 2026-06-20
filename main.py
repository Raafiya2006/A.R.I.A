from core.brain import think
from agents.voice_agent import speak, listen

speak("ARIA online. How can I help you?")

while True:
    user_input = listen(duration=5)
    if user_input:
        if any(word in user_input.lower() for word in ["bye", "goodbye", "stop"]):
            speak("Goodbye.")
            break
        response = think(user_input)
        speak(response)