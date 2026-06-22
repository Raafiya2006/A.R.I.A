import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import ollama
import datetime
from agents.calendar_agent import get_today_events
from agents.email_agent import get_recent_emails
from agents.alarm import set_timer, list_alarms
from agents.app_agent import handle_app_command

def think(user_input):
    text = user_input.lower()
    now = datetime.datetime.now()
    today = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")
    agent_data = ""

    # --- APP CONTROL (runs first, no LLM needed) ---
    app_result = handle_app_command(text)
    if app_result:
        return app_result

    # --- EMAIL ---
    if any(w in text for w in ["email", "mail", "inbox", "messages", "received"]):
        try:
            emails = get_recent_emails(5)
            if emails:
                parts = [f"From {e['from'].split('<')[0].strip()}: {e['subject']}" for e in emails[:3]]
                agent_data = "REAL EMAIL DATA: " + " | ".join(parts)
            else:
                agent_data = "REAL EMAIL DATA: No unread emails."
        except Exception as e:
            agent_data = f"Email error: {e}"

    # --- CALENDAR ---
    elif any(w in text for w in ["schedule", "calendar", "events", "what do i have"]):
        try:
            events = get_today_events()
            if events:
                parts = [e['summary'] for e in events]
                agent_data = "REAL CALENDAR DATA: " + ", ".join(parts)
            else:
                agent_data = "REAL CALENDAR DATA: No upcoming events."
        except Exception as e:
            agent_data = f"Calendar error: {e}"

    # --- TIMER ---
    elif any(w in text for w in ["timer", "alarm", "remind", "minute", "seconds"]):
        set_timer(300, "Timer")
        agent_data = "ACTION DONE: Set a 5 minute timer."

    # --- TIME ---
    elif any(w in text for w in ["time", "clock"]):
        agent_data = f"REAL TIME DATA: Current time is {current_time}"

    system_msg = f"""You are ARIA, Raafiya's personal assistant. You are direct and obedient.
- Answer in ONE short sentence only. No jokes. No filler.
- Do exactly what you're asked.
- Today is {today}, time is {current_time}"""

    if agent_data:
        system_msg += f"\n{agent_data}"

    response = ollama.chat(model='phi3', messages=[
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_input}
    ])

    import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import ollama
import datetime
import re
from agents.calendar_agent import get_today_events
from agents.email_agent import get_recent_emails
from agents.alarm import set_timer, list_alarms
from agents.app_agent import handle_app_command

def think(user_input):
    text = user_input.lower()
    now = datetime.datetime.now()
    today = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")
    agent_data = ""

    # --- APP CONTROL ---
    app_result = handle_app_command(text)
    if app_result:
        return app_result

    # --- EMAIL ---
    if any(w in text for w in ["email", "mail", "inbox", "messages", "received"]):
        try:
            emails = get_recent_emails(5)
            if emails:
                parts = [f"From {e['from'].split('<')[0].strip()}: {e['subject']}" for e in emails[:3]]
                agent_data = "REAL EMAIL DATA: " + " | ".join(parts)
            else:
                agent_data = "REAL EMAIL DATA: No unread emails."
        except Exception as e:
            agent_data = f"Email error: {e}"

    # --- CALENDAR ---
    elif any(w in text for w in ["schedule", "calendar", "events", "what do i have"]):
        try:
            events = get_today_events()
            if events:
                parts = [e['summary'] for e in events]
                agent_data = "REAL CALENDAR DATA: " + ", ".join(parts)
            else:
                agent_data = "REAL CALENDAR DATA: No upcoming events."
        except Exception as e:
            agent_data = f"Calendar error: {e}"

    # --- TIMER ---
    elif any(w in text for w in ["timer", "alarm", "remind", "minute", "seconds"]):
        set_timer(300, "Timer")
        agent_data = "ACTION DONE: Set a 5 minute timer."

    # --- TIME ---
    elif any(w in text for w in ["time", "clock"]):
        agent_data = f"REAL TIME DATA: Current time is {current_time}"

    system_msg = f"""You are ARIA, Raafiya's personal assistant. Be direct and obedient.
- ONE short sentence only. No jokes. No filler. No emojis.
- Do exactly what you are asked.
- Today is {today}, time is {current_time}"""

    if agent_data:
        system_msg += f"\n{agent_data}"

    response = ollama.chat(model='phi3', messages=[
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_input}
    ], options={'num_predict': 60, 'temperature': 0.3})

    result = response['message']['content'].strip()

    for stop in ['---', 'Instruction', 'You are ', 'Note:']:
        if stop in result:
            result = result.split(stop)[0].strip()

    sentences = re.split(r'(?<=[.!?])\s', result)
    if sentences:
        result = sentences[0].strip()

    result = result.replace('"', '').replace('\n', ' ').strip()

    return result