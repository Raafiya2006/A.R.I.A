import threading
import time
import datetime
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

active_alarms = {}

def set_timer(seconds, label='Timer'):
    def _run():
        time.sleep(seconds)
        speak(f'{label} is done!')
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return f'Timer set for {seconds} seconds'

def set_alarm(hour, minute, label='Alarm'):
    def _run():
        while True:
            now = datetime.datetime.now()
            if now.hour == hour and now.minute == minute:
                speak(f'ARIA reminder: {label}')
                break
            time.sleep(30)
    alarm_id = f'{hour}:{minute:02d}'
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    active_alarms[alarm_id] = label
    return f'Alarm set for {hour}:{minute:02d} — {label}'

def cancel_alarm(hour, minute):
    alarm_id = f'{hour}:{minute:02d}'
    if alarm_id in active_alarms:
        del active_alarms[alarm_id]
        return f'Alarm at {alarm_id} cancelled'
    return 'No alarm found at that time'

def list_alarms():
    if not active_alarms:
        return 'No active alarms'
    return ', '.join([f'{k} ({v})' for k, v in active_alarms.items()])