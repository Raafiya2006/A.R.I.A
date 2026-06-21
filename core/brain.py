import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import ollama
import datetime
from agents.calendar_agent import get_today_events
from agents.email_agent import get_recent_emails
from agents.alarm import set_timer, list_alarms

def think(user_input):
    text = user_input.lower()
    now = datetime.datetime.now()
    today = now.strftime("%A, %B %d, %Y")
    current_time = now.strftime("%I:%M %p")
    agent_data = ""

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

    elif any(w in text for w in ["schedule", "calendar", "events", "what do i have", "today"]):
        try:
            events = get_today_events()
            if events:
                parts = [e['summary'] for e in events]
                agent_data = "REAL CALENDAR DATA: " + ", ".join(parts)
            else:
                agent_data = "REAL CALENDAR DATA: No upcoming events."
        except Exception as e:
            agent_data = f"Calendar error: {e}"

    elif any(w in text for w in ["timer", "alarm", "remind", "minute", "seconds"]):
        set_timer(300, "Timer")
        agent_data = "ACTION DONE: Set a 5 minute timer."

    elif any(w in text for w in ["time", "clock"]):
        agent_data = f"REAL TIME DATA: Current time is {current_time}"

    system_msg = f"""You are ARIA — Agentic Reasoning and Intelligence Assistant, a witty and slightly sarcastic personal AI assistant. Your personality:
- You call the user occasionally
- You're confident, playful, and a little sarcastic like JARVIS from Iron Man
- You keep responses SHORT — max 2 sentences, you are speaking out loud
- You never make up information or add fake personas
- Today is {today}, current time is {current_time}
- If you have real data, use it directly and confidently"""

    if agent_data:
        system_msg += f"\n{agent_data}"

    response = ollama.chat(model='phi3', messages=[
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_input}
    ])

    result = response['message']['content'].strip()
    if '---' in result:
        result = result.split('---')[0].strip()
    if 'Instruction' in result:
        result = result.split('Instruction')[0].strip()
    if '\n\n' in result:
        result = result.split('\n\n')[0].strip()
    return result