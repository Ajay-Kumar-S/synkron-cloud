from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from monitoring_engine import MonitoringEngine

BOT_TOKEN = "YOUR_REAL_TOKEN"

monitor = MonitoringEngine()


# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("SYNKRON Monitoring Bot Online.")


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
    await update.message.reply_text("Monitoring is running.")


# ---------------- ALERT CALLBACK ----------------

def alert_callback(result):

    message = f"""
🚨 {result['type']} ALERT 🚨

Telemetry:
{result['telemetry']}

Analysis:
{result['analysis']}

Probable Cause: {result['probable_cause']}
Confidence: {result['confidence']}
"""

    app.bot.send_message(chat_id=update_chat_id, text=message)


# ---------------- MAIN ----------------

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("start_monitoring", start_monitoring))
app.add_handler(CommandHandler("stop_monitoring", stop_monitoring))
app.add_handler(CommandHandler("inject", inject))
app.add_handler(CommandHandler("status", status))

monitor.set_alert_callback(lambda result:
    app.bot.send_message(chat_id=YOUR_CHAT_ID, text=str(result))
)

app.run_polling()
