import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from dotenv import load_dotenv
load_dotenv()

import threading
from core.brain import think
from agents.voice_agent import speak, listen
from agents.alarm import set_speak_fn
from agents.calendar_agent import get_today_events
from proactive.monitor import start_monitor, set_speak_fn as monitor_speak, set_events_fn
from ui.aria_ui import launch_ui, update_status, update_transcription, update_response, set_speaking

set_speak_fn(speak)
monitor_speak(speak)
set_events_fn(get_today_events)
start_monitor()

ARIA_OWN_WORDS = ["timer is done", "aria online", "shutting down", "goodbye", "timer set"]

def aria_loop():
    speak("ARIA online.")
    update_status("ONLINE")
    update_response("ARIA online. How can I help?")

    while True:
        try:
            update_status("LISTENING")
            user_input = listen(duration=7)

            if not user_input or len(user_input.strip()) < 3:
                continue
            if len(user_input.split()) < 2:
                continue
            if any(phrase in user_input.lower() for phrase in ARIA_OWN_WORDS):
                continue

            update_transcription(user_input)
            print(f"You: {user_input}")

            if any(word in user_input.lower() for word in ["bye", "goodbye", "stop aria", "shut down"]):
                update_status("OFFLINE")
                update_response("Goodbye.")
                speak("Goodbye.")
                break

            update_status("THINKING")
            response = think(user_input)

            update_response(response)
            update_status("SPEAKING")
            set_speaking(True)
            speak(response)
            set_speaking(False)

        except KeyboardInterrupt:
            speak("Shutting down.")
            break
        except Exception as e:
            print(f"Error: {e}")
            update_status("LISTENING")
            continue

# Run ARIA in background, UI in main thread
aria_thread = threading.Thread(target=aria_loop, daemon=True)
aria_thread.start()
launch_ui()