import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import ollama
import datetime
import re
import webbrowser
from core.memory import save_conversation, get_memory_context
from agents.calendar_agent import get_today_events
from agents.email_agent import get_recent_emails
from agents.alarm import set_timer, set_alarm, list_alarms
from agents.app_agent import handle_app_command
from agents.erp_agent import (get_cae_marks, get_semester_result, compare_semesters,
                               get_attendance, get_timetable, auto_login_erp, auto_login_lms)
from agents.web_agent import get_news, web_search, get_weather
from agents.system_control import (get_network_devices, volume_up, volume_down,
                                   mute, unmute, take_screenshot, lock_screen,
                                   brightness_up, brightness_down, shutdown, restart)

def think(user_input):
    text = user_input.lower()
    now = datetime.datetime.now()
    today = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")

    # --- APP CONTROL ---
    app_result = handle_app_command(text)
    if app_result:
        return app_result

    # --- WHO ARE YOU ---
    if any(w in text for w in ["who made you", "who created you", "who built you", "who are you", "what are you"]):
        return "I am ARIA, built by Raafiya Taskeen at Sathyabama Institute as a final year project."

    # --- ENHANCE ARIA ---
    if any(w in text for w in ["enhance your", "improve you", "make you better", "upgrade you", "your capabilities"]):
        return "Just keep talking to me — I learn from every conversation we have."

    # --- ERP LOGIN ---
    if any(w in text for w in ["log into erp", "open erp", "go to erp", "login erp", "erp portal", "log in erp", "erp login", "my erp", "erp"]):
        return auto_login_erp()

    # --- LMS LOGIN ---
    if any(w in text for w in ["log into lms", "open lms", "go to lms", "login lms", "my lms", "lms"]):
        return auto_login_lms()

    # --- NETWORK DEVICES ---
    if any(w in text for w in ["network devices", "connected devices", "who is on my network",
                                "devices on network", "what devices", "scan network",
                                "my network", "on my net", "connected to my", "who's on"]):
        return get_network_devices()

    # --- SCREENSHOT ---
    if any(w in text for w in ["screenshot", "take a screenshot", "capture screen", "screen shot"]):
        return take_screenshot()

    # --- LOCK SCREEN ---
    if any(w in text for w in ["lock screen", "lock my screen", "lock computer", "lock my laptop"]):
        return lock_screen()

    # --- SHUTDOWN ---
    if any(w in text for w in ["shut down", "shutdown", "turn off my laptop", "power off"]):
        return shutdown()

    # --- RESTART ---
    if any(w in text for w in ["restart", "reboot", "restart my laptop"]):
        return restart()

    # --- VOLUME ---
    if any(w in text for w in ["volume up", "increase volume", "louder", "turn up", "turn the volume up"]):
        return volume_up()

    if any(w in text for w in ["volume down", "decrease volume", "quieter", "turn down", "lower volume", "turn the volume down"]):
        return volume_down()

    if "mute" in text and "unmute" not in text:
        return mute()

    if "unmute" in text:
        return unmute()

    # --- BRIGHTNESS ---
    if any(w in text for w in ["brightness up", "increase brightness", "brighter", "turn up brightness"]):
        return brightness_up()

    if any(w in text for w in ["brightness down", "decrease brightness", "dimmer", "dim screen", "turn down brightness"]):
        return brightness_down()

    # --- SEMESTER RESULT ---
    if any(w in text for w in ["semester result", "sem result", "exam result", "final result", "end sem", "university result"]):
        sem = 5
        for i in range(1, 8):
            if f"semester {i}" in text or f"sem {i}" in text:
                sem = i
                break
        if "last" in text or "previous" in text:
            sem = 5
        try:
            return get_semester_result(sem)
        except Exception as e:
            return f"Could not fetch result: {e}"

    # --- TIMETABLE ---
    if any(w in text for w in ["timetable", "time table", "class schedule", "classes today", "what class", "show timetable", "my classes"]):
        day = None
        for d in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            if d in text:
                day = d
                break
        try:
            return get_timetable(day)
        except Exception as e:
            return f"Could not fetch timetable: {e}"

    # --- COMPARE SEMESTERS ---
    if any(w in text for w in ["improved", "compare", "comparison", "better than last", "progress", "performance"]):
        try:
            return compare_semesters()
        except Exception as e:
            return f"Could not compare: {e}"

    # --- ATTENDANCE ---
    if any(w in text for w in ["attendance", "present", "absent", "bunk"]):
        try:
            return get_attendance()
        except Exception as e:
            return f"Could not fetch attendance: {e}"

    # --- CAE MARKS ---
    if any(w in text for w in ["cae", "internal marks", "internal result", "marks", "grades", "score", "what did i get", "how much did i", "semester marks"]):
        sem = 6
        for i in range(1, 8):
            if f"semester {i}" in text or f"sem {i}" in text:
                sem = i
                break
        try:
            return get_cae_marks(sem)
        except Exception as e:
            return f"Could not fetch marks: {e}"

    # --- EMAIL ---
    if any(w in text for w in ["email", "mail", "inbox", "messages", "unread", "check my"]):
        try:
            emails = get_recent_emails(3)
            if emails:
                response = f"You have {len(emails)} unread emails. "
                for e in emails:
                    sender = e['from'].split('<')[0].strip()
                    response += f"From {sender}: {e['subject']}. "
                return response
            else:
                return "No unread emails right now."
        except Exception as e:
            return f"Could not fetch emails: {e}"

    # --- CALENDAR ---
    if any(w in text for w in ["schedule", "calendar", "events", "what do i have", "what's on"]):
        try:
            events = get_today_events()
            if events:
                names = ", ".join([e['summary'] for e in events])
                return f"You have {len(events)} upcoming events: {names}."
            else:
                return "Nothing on your calendar right now."
        except Exception as e:
            return f"Could not fetch calendar: {e}"

    # --- WAR / CONFLICT NEWS ---
    if any(w in text for w in ["war", "conflict", "attack", "missile", "bombing", "military", "troops", "invasion", "battle"]):
        try:
            return get_news(user_input + " 2026")
        except Exception as e:
            return f"Could not fetch news: {e}"

    # --- NEWS ---
    if any(w in text for w in ["news", "headlines", "what's happening", "current events"]):
        topic = "world news today"
        if "india" in text:
            topic = "india news today"
        elif "tech" in text or "technology" in text:
            topic = "technology news today"
        elif "sports" in text:
            topic = "sports news today"
        elif "cricket" in text:
            topic = "cricket news today"
        elif "trump" in text or "president" in text:
            topic = "US president Trump news today"
        try:
            return get_news(topic)
        except Exception as e:
            return f"Could not fetch news: {e}"

    # --- WEATHER ---
    if any(w in text for w in ["weather", "temperature", "rain", "forecast"]):
        city = "Chennai"
        cities = ["mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata"]
        for c in cities:
            if c in text:
                city = c.title()
                break
        try:
            return get_weather(city)
        except Exception as e:
            return f"Could not fetch weather: {e}"

    # --- SPECIFIC FACTUAL QUESTIONS ---
    specific_triggers = [
        "what did", "what has", "who did", "who is", "who was",
        "tell me about", "what happened", "when did", "where is",
        "how much", "what are the", "latest", "recent", "currently",
        "news about", "update on", "what's happening with", "how many",
        "which", "why did", "why is", "when is", "where did"
    ]
    if any(w in text for w in specific_triggers):
        query = user_input
        for trigger in specific_triggers:
            if trigger in text:
                after = text.split(trigger)[-1].strip()
                if len(after) > 2:
                    query = after
                    break
        try:
            result = web_search(query)
            if result and len(result) > 10:
                return result
        except:
            pass

    # --- TIMER ---
    if any(w in text for w in ["timer", "pomodoro"]):
        minutes = 5
        seconds_direct = None
        words = text.split()
        for i, word in enumerate(words):
            if word.isdigit():
                num = int(word)
                if i + 1 < len(words):
                    next_word = words[i + 1]
                    if "second" in next_word:
                        seconds_direct = num
                    elif "minute" in next_word:
                        minutes = num
                else:
                    minutes = num
                break
        if seconds_direct:
            set_timer(seconds_direct, f"{seconds_direct} second timer")
            return f"Timer set for {seconds_direct} seconds."
        else:
            set_timer(minutes * 60, f"{minutes} minute timer")
            return f"Timer set for {minutes} minutes."

    # --- ALARM ---
    if any(w in text for w in ["set an alarm", "wake me", "alarm for", "remind me at"]):
        return "To set an alarm say the time like: set alarm for 7 AM."

    # --- LIST ALARMS ---
    if "list alarm" in text or "active alarm" in text or "what alarm" in text:
        return list_alarms()

    # --- TIME ---
    if any(w in text for w in ["what time", "current time", "what's the time"]):
        return f"It's {current_time}."

    # --- DATE ---
    if any(w in text for w in ["what day", "today's date", "what date", "what is today"]):
        return f"Today is {today}."

    # --- BIRTHDAY ---
    if "birthday" in text:
        birthday = datetime.datetime(now.year, 8, 22)
        if birthday < now:
            birthday = datetime.datetime(now.year + 1, 8, 22)
        days = (birthday - now).days
        return f"Your birthday is in {days} days, on August 22nd."

    # --- MEMORY RECALL ---
    if any(w in text for w in ["remember", "recall", "what did i ask", "last time", "previously", "did i tell you"]):
        context = get_memory_context(user_input)
        if context:
            return f"From our past conversations: {context[:300]}"
        return "I don't have any relevant memories yet."

    # --- GENERAL LLM ---
    memory_context = get_memory_context(user_input)

    system_msg = f"""You are ARIA, built by Raafiya. ONE sentence max. Casual and direct like a friend.
Never say Microsoft, never say developed by, never say as an AI. You are ARIA.
Today is {today}, time is {current_time}.
{f'Context: {memory_context[:150]}' if memory_context else ''}"""

    try:
        response = ollama.chat(model='phi3', messages=[
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_input}
        ], options={'num_predict': 60, 'temperature': 0.3})

        result = response['message']['content'].strip()

        for stop in ['---', 'Instruction', 'You are ', 'Note:', 'Microsoft',
                     'As an AI', "I'm sorry", 'I apologize', 'developed by',
                     'I cannot perform', 'I am unable']:
            if stop.lower() in result.lower():
                idx = result.lower().index(stop.lower())
                result = result[:idx].strip()

        sentences = re.split(r'(?<=[.!?])\s', result)
        if sentences:
            result = sentences[0].strip()

        result = result.replace('"', '').replace('\n', ' ').strip()

        if not result or len(result) < 3:
            result = "I'm not sure how to help with that yet."

        save_conversation(user_input, result)
        return result

    except Exception:
        return "Sorry, my brain is busy right now."