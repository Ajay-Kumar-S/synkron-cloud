import os
from diagnostic_mode import handle_diagnostic
from telegram_alert import send_telegram_message


def process_message(user_input):

    lower = user_input.lower().strip()

    # Diagnostic mode first
    diagnostic_response = handle_diagnostic(user_input)
    if diagnostic_response:
        return diagnostic_response

    if lower == "test telegram":
        send_telegram_message("🚀 SYNKRON Telegram Connected Successfully")
        return "Telegram test message sent."

    return "Command not recognized."


# ===============================
# LOCAL CLI MODE ONLY
# ===============================

if __name__ == "__main__" and not os.environ.get("CLOUD_MODE"):

    print("Advanced Productivity + Diagnostic AI Ready\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        response = process_message(user_input)

        if response:
            print("\nAI:", response)
