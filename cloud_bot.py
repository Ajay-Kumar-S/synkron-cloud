import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from monitoring_engine import MonitoringEngine

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

if not CHAT_ID:
    raise ValueError("CHAT_ID environment variable not set")

monitor = MonitoringEngine()

app = ApplicationBuilder().token(BOT_TOKEN).build()


# ================= COMMANDS =================

async def start(update, context):
    await update.message.reply_text("🚀 SYNKRON Cloud Monitoring Online")


async def start_monitoring(update, context):
    result = monitor.start()
    await update.message.reply_text(result)


async def stop_monitoring(update, context):
    result = monitor.stop()
    await update.message.reply_text(result)


async def inject(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /inject drive_fault")
        return

    fault = context.args[0]
    monitor.inject_fault(fault)
    await update.message.reply_text(f"Injected fault: {fault}")


async def status(update, context):
    await update.message.reply_text("Monitoring service active.")


# ================= ALERT CALLBACK =================

def alert_callback(result):

    if result["type"] == "RECOVERY":
        message = f"✅ SYSTEM RECOVERY\nPrevious Fault: {result['previous_fault']}"
    else:
        message = (
            f"🚨 {result['type']} ALERT 🚨\n\n"
            f"Telemetry:\n{result['telemetry']}\n\n"
            f"Analysis:\n{result['analysis']}\n\n"
            f"Probable Cause: {result['probable_cause']}\n"
            f"Confidence: {result['confidence']}"
        )

    asyncio.run(
        app.bot.send_message(chat_id=CHAT_ID, text=message)
    )


monitor.set_alert_callback(alert_callback)


# ================= START BOT =================

if __name__ == "__main__":

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_monitoring", start_monitoring))
    app.add_handler(CommandHandler("stop_monitoring", stop_monitoring))
    app.add_handler(CommandHandler("inject", inject))
    app.add_handler(CommandHandler("status", status))

    print("🚀 SYNKRON Cloud Bot Running (Long Polling Mode)")

    app.run_polling()
