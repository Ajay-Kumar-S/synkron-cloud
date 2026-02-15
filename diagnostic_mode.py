from monitoring_engine import MonitoringEngine
from telegram_alert import send_telegram_message


diagnostic_active = False
monitor = MonitoringEngine()


# ---------------------------------
# ALERT CALLBACK
# ---------------------------------

def alert_printer(result):

    if result["type"] == "RECOVERY":

        message = (
            "✅ SYSTEM RECOVERY\n\n"
            f"Previous Fault: {result['previous_fault']}"
        )

        print(message)
        send_telegram_message(message)
        return

    message = (
        f"🚨 {result['type']} ALERT 🚨\n\n"
        f"Telemetry:\n{result['telemetry']}\n\n"
        f"Analysis:\n{result['analysis']}\n\n"
        f"Probable Cause: {result['probable_cause']}\n"
        f"Confidence: {result['confidence']}\n\n"
        f"AI Summary:\n{result['ai_report'][:500]}"
    )

    print(message)
    send_telegram_message(message)


monitor.set_alert_callback(alert_printer)


# ---------------------------------
# MODE CONTROL
# ---------------------------------

def start_diagnostic_mode():
    global diagnostic_active
    diagnostic_active = True
    return (
        "Diagnostic Mode Activated.\n\n"
        "Commands:\n"
        "- start monitoring\n"
        "- stop monitoring\n"
        "- inject drive_fault\n"
        "- inject none\n"
        "- exit diagnostic\n"
    )


def exit_diagnostic_mode():
    global diagnostic_active
    monitor.stop()
    diagnostic_active = False
    return "Exited Diagnostic Mode."


def handle_diagnostic(user_input):

    global diagnostic_active

    lower = user_input.lower().strip()

    if lower == "diagnose":
        return start_diagnostic_mode()

    if not diagnostic_active:
        return None

    if lower == "exit diagnostic":
        return exit_diagnostic_mode()

    if lower == "start monitoring":
        return monitor.start()

    if lower == "stop monitoring":
        return monitor.stop()

    if lower.startswith("inject"):
        fault = lower.replace("inject", "").strip()

        if fault == "none":
            monitor.inject_fault("none")
            return "Fault cleared."

        monitor.inject_fault(fault)
        return f"Injected fault mode: {fault}"

    return "Diagnostic command not recognized."
