import random
import time


class TelemetryEngine:

    def __init__(self):
        self.running = False
        self.fault_mode = None

    def inject_fault(self, fault_name):
        self.fault_mode = fault_name

    def generate_data(self):

        data = {
            "motor_current": round(random.uniform(5, 15), 2),
            "brake_voltage": 230,
            "drive_dc_bus": 560,
            "encoder_speed": round(random.uniform(900, 1000), 2),
            "safety_chain": True,
            "door_closed": True,
            "overload_percent": round(random.uniform(20, 60), 1)
        }

        # Fault Injection
        if self.fault_mode == "drive_fault":
            data["drive_dc_bus"] = 0
            data["motor_current"] = 0

        if self.fault_mode == "brake_fault":
            data["brake_voltage"] = 0

        if self.fault_mode == "overload":
            data["overload_percent"] = 110

        if self.fault_mode == "safety_chain_open":
            data["safety_chain"] = False

        return data

    def analyze_stream(self, data):

        issues = []

        if data["drive_dc_bus"] == 0:
            issues.append("Drive DC bus voltage missing.")

        if data["brake_voltage"] == 0:
            issues.append("Brake voltage absent.")

        if not data["safety_chain"]:
            issues.append("Safety chain open.")

        if data["overload_percent"] > 100:
            issues.append("Overload condition detected.")

        if data["motor_current"] == 0 and data["encoder_speed"] == 0:
            issues.append("Motor not running.")

        if not issues:
            return "Telemetry normal."

        return "\n".join(issues)
