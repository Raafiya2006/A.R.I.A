from agents.alarm import set_timer, set_alarm, list_alarms

# Test 1 — timer
print(set_timer(5, 'Test timer'))

# Test 2 — alarm
print(list_alarms())

# Keep the script running so the timer can fire
import time
print("Waiting for timer...")
time.sleep(10)
print("Done!")