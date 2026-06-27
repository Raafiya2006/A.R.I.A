import threading
import time
import datetime

# Store reference to ARIA's speak function
_speak_fn = None

def set_speak_fn(fn):
    global _speak_fn
    _speak_fn = fn

def _speak(text):
    if _speak_fn:
        _speak_fn(text)
    else:
        print(f"TIMER: {text}")

active_alarms = {}

def set_timer(seconds, label='Timer'):
    def _run():
        time.sleep(seconds)
        _speak(f"{label} is done!")
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return f"Timer set for {seconds} seconds"

def set_alarm(hour, minute, label='Alarm'):
    def _run():
        while True:
            now = datetime.datetime.now()
            if now.hour == hour and now.minute == minute:
                _speak(f"ARIA reminder: {label}")
                break
            time.sleep(30)
    alarm_id = f'{hour}:{minute:02d}'
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    active_alarms[alarm_id] = label
    return f"Alarm set for {hour}:{minute:02d}"

def cancel_alarm(hour, minute):
    alarm_id = f'{hour}:{minute:02d}'
    if alarm_id in active_alarms:
        del active_alarms[alarm_id]
        return f"Alarm at {alarm_id} cancelled"
    return "No alarm found at that time"

def list_alarms():
    if not active_alarms:
        return "No active alarms"
    return ", ".join([f"{k} ({v})" for k, v in active_alarms.items()])