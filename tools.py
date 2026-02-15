def detect_intent(message: str):

    message_lower = message.lower()

    if "free slot" in message_lower or "available" in message_lower or "find free" in message_lower:
        return "find_free"

    if "reschedule" in message_lower or "move" in message_lower:
        return "reschedule"

    if "cancel" in message_lower or "delete" in message_lower:
        return "cancel"

    if "schedule" in message_lower or "book" in message_lower:
        return "intelligent_meeting"

    if "show" in message_lower or "what are my meetings" in message_lower or "do i have" in message_lower:
        return "view_schedule"

    if "remember" in message_lower or "note" in message_lower:
        return "store_memory"

    return "general"
