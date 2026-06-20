from agents.voice_agent import speak, listen

speak("Hello, I am ARIA. Say something.")
user_input = listen(duration=5)
speak(f"You said: {user_input}")