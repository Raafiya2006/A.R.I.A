from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle, os, datetime

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as f:
            pickle.dump(creds, f)
    return build('calendar', 'v3', credentials=creds)

def get_today_events():
    service = get_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=end,
        maxResults=20, singleEvents=True, orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def add_event(title, date_str, time_str=None):
    service = get_service()
    event = {
        'summary': title,
        'start': {'date': date_str} if not time_str else {'dateTime': f'{date_str}T{time_str}:00', 'timeZone': 'Asia/Kolkata'},
        'end': {'date': date_str} if not time_str else {'dateTime': f'{date_str}T{time_str}:00', 'timeZone': 'Asia/Kolkata'},
    }
    service.events().insert(calendarId='primary', body=event).execute()
    return f'Added: {title} on {date_str}'