import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

import threading
import time
import datetime
import pygetwindow as gw
import psutil

# Will be set from main.py
_speak_fn = None
_get_events_fn = None

def set_speak_fn(fn):
    global _speak_fn
    _speak_fn = fn

def set_events_fn(fn):
    global _get_events_fn
    _get_events_fn = fn

def speak(text):
    if _speak_fn:
        _speak_fn(text)
    else:
        print(f"PROACTIVE: {text}")

def get_active_window():
    try:
        window = gw.getActiveWindow()
        if window:
            return window.title.lower()
        return ""
    except:
        return ""

def get_upcoming_exams():
    """Check calendar for exams in next 3 days"""
    try:
        if _get_events_fn:
            events = _get_events_fn()
            urgent = []
            now = datetime.datetime.now()
            for e in events:
                summary = e.get('summary', '').lower()
                if any(w in summary for w in ['exam', 'test', 'quiz', 'assignment', 'submission', 'deadline', 'viva']):
                    urgent.append(e['summary'])
            return urgent
        return []
    except:
        return []

def check_youtube_usage(usage_tracker):
    """Track YouTube usage and warn if too long"""
    window = get_active_window()
    is_youtube = 'youtube' in window or 'youtu' in window
    
    if is_youtube:
        usage_tracker['youtube_seconds'] += 30  # Check every 30 seconds
        minutes = usage_tracker['youtube_seconds'] // 60
        
        if minutes >= 40 and not usage_tracker.get('warned_40'):
            exams = get_upcoming_exams()
            if exams:
                speak(f"Raafiya, you've been on YouTube for {minutes} minutes. You have {exams[0]} coming up. Maybe take a break?")
            else:
                speak(f"Raafiya, you've been on YouTube for {minutes} minutes. Just a heads up.")
            usage_tracker['warned_40'] = True
        
        elif minutes >= 20 and not usage_tracker.get('warned_20'):
            speak(f"You've been on YouTube for 20 minutes, Raafiya.")
            usage_tracker['warned_20'] = True
    else:
        # Reset if they left YouTube
        if usage_tracker['youtube_seconds'] > 0:
            usage_tracker['youtube_seconds'] = 0
            usage_tracker['warned_20'] = False
            usage_tracker['warned_40'] = False

def morning_briefing():
    """Give morning briefing at 8am"""
    try:
        now = datetime.datetime.now()
        if now.hour == 8 and now.minute < 1:
            events = get_upcoming_exams()
            greeting = f"Good morning Raafiya! Today is {now.strftime('%A, %B %d')}."
            if events:
                greeting += f" You have {len(events)} important events coming up: {', '.join(events[:2])}."
            else:
                greeting += " You have no urgent deadlines today."
            speak(greeting)
            return True
    except:
        pass
    return False

def check_idle():
    """Detect if user has been idle for too long"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        return cpu < 5
    except:
        return False

def run_monitor():
    """Main monitoring loop — runs in background"""
    print("Proactive monitor started...")
    
    usage_tracker = {
        'youtube_seconds': 0,
        'warned_20': False,
        'warned_40': False,
    }
    
    briefing_done = False
    last_briefing_date = None
    check_count = 0
    
    while True:
        try:
            now = datetime.datetime.now()
            
            # Morning briefing once per day at 8am
            if now.hour == 8 and now.minute == 0:
                today = now.strftime("%Y-%m-%d")
                if last_briefing_date != today:
                    morning_briefing()
                    last_briefing_date = today
            
            # Check YouTube every 30 seconds
            check_youtube_usage(usage_tracker)
            
            # Check for urgent exams every 10 minutes
            check_count += 1
            if check_count >= 20:  # 20 * 30 seconds = 10 minutes
                check_count = 0
                exams = get_upcoming_exams()
                now_hour = datetime.datetime.now().hour
                if exams and 9 <= now_hour <= 21:
                    # Only remind once per hour
                    if not usage_tracker.get(f'exam_reminded_{now_hour}'):
                        speak(f"Reminder: {exams[0]} is coming up soon!")
                        usage_tracker[f'exam_reminded_{now_hour}'] = True
            
            time.sleep(30)
            
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(30)

def start_monitor():
    """Start monitor in background thread"""
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    print("Proactive monitor running in background")
    return thread