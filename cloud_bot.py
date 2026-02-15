import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from monitoring_engine import MonitoringEngine


# =====================================================
# ENVIRONMENT VARIABLES
# =====================================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

if not CHAT_ID:
    raise ValueError("CHAT_ID environment variable not set")


# =====================================================
# INIT
# =====================================================

monitor = MonitoringEngine()

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()


# =====================================================
# TELEGRAM COMMANDS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 SYNKRON Cloud Monitoring Online")


async def start_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = monitor.start()
    await update.message.reply_text(result)


async def stop_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = monitor.stop()
    await update.message.reply_text(result)


async def inject(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage: /inject drive_fault")
        return

    fault = context.args[0]
    monitor.inject_fault(fault)

    await update.message.reply_text(f"Injected fault: {fault}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Monitoring service active.")


# =====================================================
# ALERT CALLBACK → TELEGRAM PUSH
# =====================================================

def alert_callback(result):

    if result["type"] == "RECOVERY":

        message = (
            "✅ SYSTEM RECOVERY\n\n"
            f"Previous Fault: {result['previous_fault']}"
        )

        telegram_app.bot.send_message(chat_id=CHAT_ID, text=message)
        return

    message = (
        f"🚨 {result['type']} ALERT 🚨\n\n"
        f"Telemetry:\n{result['telemetry']}\n\n"
        f"Analysis:\n{result['analysis']}\n\n"
        f"Probable Cause: {result['probable_cause']}\n"
        f"Confidence: {result['confidence']}"
    )

    telegram_app.bot.send_message(chat_id=CHAT_ID, text=message)


monitor.set_alert_callback(alert_callback)


# =====================================================
# FLASK ROUTES
# =====================================================

@app.route("/", methods=["GET"])
def home():
    return "SYNKRON Cloud Bot Running"


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"


# =====================================================
# STARTUP
# =====================================================

if __name__ == "__main__":

    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("start_monitoring", start_monitoring))
    telegram_app.add_handler(CommandHandler("stop_monitoring", stop_monitoring))
    telegram_app.add_handler(CommandHandler("inject", inject))
    telegram_app.add_handler(CommandHandler("status", status))

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

