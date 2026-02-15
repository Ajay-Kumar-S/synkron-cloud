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
