import threading
import time

from telemetry_engine import TelemetryEngine
from bayesian_engine import BayesianModel
from deep_analysis import deep_root_analysis
from learning_engine import store_case


class MonitoringEngine:

    def __init__(self):

        self.telemetry = TelemetryEngine()
        self.bayes = BayesianModel()

        self.active = False
        self.thread = None
        self.alert_callback = None

        self.current_state = "NORMAL"
        self.current_fault = None

    # ---------------------------------
    # PUBLIC CONTROL
    # ---------------------------------

    def start(self):

        if self.active:
            return "Monitoring already running."

        self.active = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        return "Continuous Monitoring Started."

    def stop(self):
        self.active = False
        return "Monitoring stopped."

    def inject_fault(self, fault):
        self.telemetry.inject_fault(fault)

    def set_alert_callback(self, callback):
        self.alert_callback = callback

    # ---------------------------------
    # MONITOR LOOP
    # ---------------------------------

    def _monitor_loop(self):

        while self.active:

            try:
                result = self._run_cycle()

                if result and self.alert_callback:
                    self.alert_callback(result)

            except Exception as e:
                print("Monitoring Error:", e)

            time.sleep(1)

    # ---------------------------------
    # STATE MACHINE
    # ---------------------------------

    def _run_cycle(self):

        data = self.telemetry.generate_data()
        analysis = self.telemetry.analyze_stream(data)

        if analysis == "Telemetry normal.":

            if self.current_state != "NORMAL":

                recovery = {
                    "type": "RECOVERY",
                    "previous_fault": self.current_fault
                }

                self.current_state = "NORMAL"
                self.current_fault = None

                return recovery

            return None

        # anomaly detected
        self.bayes.update(analysis)
        ranked = self.bayes.get_ranked()

        top_cause = ranked[0][0]
        confidence = round(ranked[0][1], 3)

        severity = self._determine_severity(data)

        if self.current_fault != top_cause or self.current_state != severity:

            store_case("telemetry_event", top_cause)

            report = deep_root_analysis(top_cause)

            self.current_fault = top_cause
            self.current_state = severity

            return {
                "type": severity,
                "telemetry": data,
                "analysis": analysis,
                "probable_cause": top_cause,
                "confidence": confidence,
                "ai_report": report
            }

        return None

    def _determine_severity(self, data):

        if data["drive_dc_bus"] == 0:
            return "CRITICAL"

        if data["brake_voltage"] == 0:
            return "CRITICAL"

        if not data["safety_chain"]:
            return "CRITICAL"

        if data["overload_percent"] > 100:
            return "WARNING"

        return "WARNING"
