import dateparser
from calendar_tool import create_event
from diagnostic_mode import handle_diagnostic

# ==============================
# USER SESSION STORAGE
# ==============================

user_sessions = {}


def reset_session(chat_id):
    if chat_id in user_sessions:
        del user_sessions[chat_id]


# ==============================
# INTENT DETECTION
# ==============================

def detect_intent(message):

    msg = message.lower()

    if "schedule" in msg or "meeting" in msg:
        return "scheduling"

    if any(word in msg for word in ["door", "drive", "fault", "blower", "motor"]):
        return "diagnostic"

    if msg in ["exit", "cancel"]:
        return "exit"

    return None


# ==============================
# MAIN ROUTER (THIS WAS MISSING)
# ==============================

def process_message(chat_id, message):

    # Continue existing session
    if chat_id in user_sessions:

        mode = user_sessions[chat_id]["mode"]

        if mode == "scheduling":
            return handle_scheduling(chat_id, message)

        if mode == "diagnostic":
            return handle_diagnostic(message)

    # Detect new intent
    intent = detect_intent(message)

    if intent == "scheduling":

        user_sessions[chat_id] = {
            "mode": "scheduling",
            "step": "title",
            "data": {}
        }

        return "What is the meeting title?"

    if intent == "diagnostic":

        user_sessions[chat_id] = {
            "mode": "diagnostic"
        }

        return "Diagnostic mode activated. Describe the issue."

    if intent == "exit":
        reset_session(chat_id)
        return "Session closed."

    return "Command not recognized."


# ==============================
# SCHEDULING ENGINE
# ==============================

def handle_scheduling(chat_id, message):

    session = user_sessions[chat_id]
    step = session["step"]

    if step == "title":
        session["data"]["title"] = message
        session["step"] = "time"
        return "When is the meeting?"

    elif step == "time":
        dt = dateparser.parse(message)

        if not dt:
            return "Could not understand date/time. Please re-enter."

        session["data"]["datetime"] = dt
        session["step"] = "duration"
        return "Duration (e.g., 1 hour)?"

    elif step == "duration":
        session["data"]["duration"] = message
        session["step"] = "attendees"
        return "Enter attendee email."

    elif step == "attendees":
        session["data"]["attendees"] = message
        session["step"] = "confirm"

        d = session["data"]

        return (
            f"Confirm meeting?\n\n"
            f"Title: {d['title']}\n"
            f"When: {d['datetime']}\n"
            f"Duration: {d['duration']}\n"
            f"Attendee: {d['attendees']}\n\n"
            f"Type 'confirm' to schedule."
        )

    elif step == "confirm":

        if message.lower() == "confirm":

            d = session["data"]

            meeting_data = {
                "title": d["title"],
                "datetime": d["datetime"],
                "duration": d["duration"],
                "attendees": d["attendees"]
            }

            event_link = create_event(meeting_data)

            reset_session(chat_id)

            return f"Meeting created.\n{event_link}"

        else:
            return "Type 'confirm' to create meeting."
