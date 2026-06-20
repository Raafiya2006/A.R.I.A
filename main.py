from agents.email_agent import get_recent_emails

emails = get_recent_emails()
if emails:
    for e in emails:
        print(f"From: {e['from']}")
        print(f"Subject: {e['subject']}")
        print(f"Preview: {e['snippet']}")
        print("---")
else:
    print('No unread emails')