import requests

BOT_TOKEN = "8478065355:AAHuOL-hLUotJDBIzPzTiUTGXfF1dUguAG8"
CHAT_ID = "923533973"


def send_telegram_message(message):

    print("Sending to Telegram...")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload)
        print("Response:", response.text)
    except Exception as e:
        print("Telegram Error:", e)
