import re
import dateparser
import datetime

from calendar_tool import (
    create_event,
    list_events,
    cancel_event_by_title,
    reschedule_event_by_title,
    generate_block_summary
)

from diagnostic_mode import (
    start_diagnostic_mode,
    exit_diagnostic_mode,
    process_diagnostic_input
)

# =========================================================
# ---------------- GLOBAL STATES --------------------------
# =========================================================

preferred_hours = {}
pending_meeting = None
diagnostic_mode_active = False


# =========================================================
# ---------------- BASIC EXTRACTION -----------------------
# =========================================================

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group() if match else None


def extract_duration(text):
    match = re.search(r'(\d+)\s*(hour|hours)', text.lower())
    if match:
        return int(match.group(1))
    return 1


def extract_datetime(text):

    settings = {
        'PREFER_DATES_FROM': 'future',
        'TIMEZONE': 'Asia/Kolkata',
        'RETURN_AS_TIMEZONE_AWARE': False
    }

    parsed = dateparser.parse(text, settings=settings)
    if parsed:
        return parsed

    patterns = [
        r'(today\s*\d*\s*(am|pm)?)',
        r'(tomorrow\s*\d*\s*(am|pm)?)',
        r'(next\s+\w+\s*\d*\s*(am|pm)?)',
        r'(\d{1,2}\s*(am|pm))'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group()
            parsed = dateparser.parse(candidate, settings=settings)
            if parsed:
                return parsed

    return None


def extract_title(text):

    text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)
    text = re.sub(r'\d{1,2}\s*(am|pm)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*(hour|hours)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'tomorrow|today|next\s+\w+', '', text, flags=re.IGNORECASE)

    text = re.sub(
        r'schedule|book|meeting|with|at|for|to|reschedule|move|cancel|delete',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r'\s+', ' ', text).strip()

    return text.title()


# =========================================================
# ---------------- DIAGNOSTIC MODE ------------------------
# =========================================================

def handle_diagnostic(user_input):

    global diagnostic_mode_active

    lower = user_input.lower()

    # Activate diagnostic mode
    if lower == "diagnose":
        diagnostic_mode_active = True
        return start_diagnostic_mode()

    # Exit diagnostic mode
    if lower == "exit diagnostic":
        diagnostic_mode_active = False
        return exit_diagnostic_mode()

    # If diagnostic mode active → route input
    if diagnostic_mode_active:
        return process_diagnostic_input(user_input)

    return None


# =========================================================
# ---------------- SCHEDULING SYSTEM ----------------------
# =========================================================

def start_intelligent_meeting(user_input):

    global pending_meeting

    parsed_dt = extract_datetime(user_input)
    email = extract_email(user_input)
    duration = extract_duration(user_input)

    if not parsed_dt:
        return "Could not understand date/time."

    if not email:
        return "Missing attendee email."

    pending_meeting = {
        "title": extract_title(user_input),
        "parsed_datetime": parsed_dt,
        "duration": duration,
        "agenda": "Auto-created",
        "attendees": email
    }

    return (
        f"Title: {pending_meeting['title']}\n"
        f"When: {parsed_dt.strftime('%B %d %I:%M %p')}\n"
        f"Duration: {duration} hour\n"
        f"Attendees: {email}\n\n"
        "Type 'confirm' to schedule."
    )


def finalize_intelligent_meeting():

    global pending_meeting

    if not pending_meeting:
        return "No meeting pending."

    hour = pending_meeting["parsed_datetime"].hour
    preferred_hours[hour] = preferred_hours.get(hour, 0) + 1

    result = create_event(pending_meeting)

    pending_meeting = None

    return result


def handle_view_schedule(user_input):

    now = datetime.datetime.now()

    if "tomorrow" in user_input.lower():
        start = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0)
        end = start + datetime.timedelta(days=1)
    else:
        start = now.replace(hour=0, minute=0)
        end = start + datetime.timedelta(days=1)

    return list_events(start, end)


def handle_find_free_slot(user_input):

    now = datetime.datetime.now()

    target_date = now
    if "tomorrow" in user_input.lower():
        target_date = now + datetime.timedelta(days=1)

    duration = extract_duration(user_input)

    range_match = re.search(r'between (\d{1,2}) and (\d{1,2})', user_input.lower())

    range_start = None
    range_end = None

    if range_match:
        start_hour = int(range_match.group(1))
        end_hour = int(range_match.group(2))
        range_start = target_date.replace(hour=start_hour, minute=0)
        range_end = target_date.replace(hour=end_hour, minute=0)

    blocks = generate_block_summary(target_date, duration, range_start, range_end)

    if not blocks:
        return "No suitable free slots available."

    response = "Free time blocks:\n"

    for start, end in blocks:
        response += f"{start.strftime('%H:%M')} – {end.strftime('%H:%M')}\n"

    response += "\nSuggested start times:\n"

    suggestions = []

    for start, end in blocks:

        block_hours = int((end - start).total_seconds() / 3600)

        suggestions.append(start)

        if block_hours >= duration * 2:
            middle = start + datetime.timedelta(hours=block_hours // 2)
            suggestions.append(middle)

        suggestions.append(end - datetime.timedelta(hours=duration))

    suggestions.sort(key=lambda s: -preferred_hours.get(s.hour, 0))

    final_suggestions = []

    for slot in suggestions[:5]:
        end_time = slot + datetime.timedelta(hours=duration)
        final_suggestions.append(
            f"{slot.strftime('%H:%M')} – {end_time.strftime('%H:%M')}"
        )

    response += "\n".join(final_suggestions)

    return response


def handle_cancel(user_input):
    return cancel_event_by_title(extract_title(user_input))


def handle_reschedule(user_input):

    parsed_dt = extract_datetime(user_input)
    if not parsed_dt:
        return "Could not understand new date/time."

    return reschedule_event_by_title(extract_title(user_input), parsed_dt)
