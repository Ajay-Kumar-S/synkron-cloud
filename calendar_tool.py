import os
import base64

if os.environ.get("GOOGLE_CREDENTIALS"):

    decoded = base64.b64decode(os.environ["GOOGLE_CREDENTIALS"]).decode("utf-8")

    with open("credentials.json", "w") as f:
        f.write(decoded)
import datetime
import os.path
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/calendar']

WORK_START_HOUR = 9
WORK_START_MINUTE = 30
WORK_END_HOUR = 18
LUNCH_START = 13
LUNCH_END = 14


def authenticate():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If credentials exist but expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # If no valid credentials, login again
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)



# ---------------- GENERATE CANDIDATE SLOTS ----------------
def generate_block_summary(date, duration_hours=1, range_start=None, range_end=None):

    service = authenticate()

    work_start = date.replace(hour=9, minute=30, second=0)
    work_end = date.replace(hour=18, minute=0, second=0)

    if range_start:
        work_start = max(work_start, range_start)

    if range_end:
        work_end = min(work_end, range_end)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=work_start.isoformat() + 'Z',
        timeMax=work_end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    busy = []

    for event in events:
        start = datetime.datetime.fromisoformat(event['start']['dateTime'])
        end = datetime.datetime.fromisoformat(event['end']['dateTime'])
        busy.append((start, end))

    busy.sort()

    free_blocks = []
    current = work_start

    for busy_start, busy_end in busy:
        if current < busy_start:
            free_blocks.append((current, busy_start))
        current = max(current, busy_end)

    if current < work_end:
        free_blocks.append((current, work_end))

    # Filter by duration + soft lunch logic
    valid_blocks = []

    for start, end in free_blocks:
        if (end - start).total_seconds() >= duration_hours * 3600:

            # Soft lunch avoidance: split block if it crosses lunch
            if start.hour < 13 and end.hour > 14:
                valid_blocks.append((start, start.replace(hour=13, minute=0)))
                valid_blocks.append((start.replace(hour=14, minute=0), end))
            else:
                valid_blocks.append((start, end))

    return valid_blocks



# ---------------- SUGGEST ALTERNATIVES ----------------
def suggest_alternatives(date, duration_hours=1):

    slots = generate_candidate_slots(date, duration_hours)

    if not slots:
        return "Conflict detected. No alternative slots available."

    suggestions = []

    for slot in slots[:5]:
        end_time = slot + datetime.timedelta(hours=duration_hours)
        suggestions.append(
            f"{slot.strftime('%H:%M')} – {end_time.strftime('%H:%M')}"
        )

    return "Conflict detected.\nNearest available slots:\n" + "\n".join(suggestions)


# ---------------- CREATE EVENT ----------------
def create_event(meeting_data):

    service = authenticate()

    event_datetime = meeting_data["parsed_datetime"]
    duration_hours = meeting_data["duration"]

    end_time = event_datetime + datetime.timedelta(hours=duration_hours)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=event_datetime.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    if events_result.get('items'):
        return suggest_alternatives(event_datetime.date(), duration_hours)

    event = {
        'summary': meeting_data['title'],
        'description': meeting_data['agenda'],
        'start': {
            'dateTime': event_datetime.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [
            {'email': email.strip()}
            for email in meeting_data['attendees'].split(',')
        ],
    }

    created_event = service.events().insert(
        calendarId='primary',
        body=event
    ).execute()

    return "Meeting created successfully.\n" + created_event.get('htmlLink')


# ---------------- LIST EVENTS ----------------
def list_events(start_time, end_time):

    service = authenticate()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return "No meetings found."

    response = ""
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        response += f"{start} — {event.get('summary', 'No Title')}\n"

    return response


# ---------------- CANCEL ----------------
def cancel_event_by_title(title):

    service = authenticate()

    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=30)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=future.isoformat() + 'Z',
        q=title,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return "No matching meeting found."

    event = events[0]

    service.events().delete(
        calendarId='primary',
        eventId=event['id']
    ).execute()

    return f"Meeting '{event['summary']}' cancelled successfully."


# ---------------- RESCHEDULE ----------------
def reschedule_event_by_title(title, new_datetime):

    service = authenticate()

    now = datetime.datetime.now()
    future = now + datetime.timedelta(days=30)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=future.isoformat() + 'Z',
        q=title,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return "No matching meeting found."

    event = events[0]

    event['start']['dateTime'] = new_datetime.isoformat()
    event['end']['dateTime'] = (
        new_datetime + datetime.timedelta(hours=1)
    ).isoformat()

    service.events().update(
        calendarId='primary',
        eventId=event['id'],
        body=event
    ).execute()

    return f"Meeting '{event['summary']}' rescheduled successfully."
