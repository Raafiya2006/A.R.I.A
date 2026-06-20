from agents.calendar_agent import get_today_events, add_event

# Add a test event
print(add_event('ARIA Test Event', '2026-06-25', '10:00'))

# Now fetch and show events
events = get_today_events()
if events:
    for e in events:
        print(e['summary'], e['start'])
else:
    print('No upcoming events')