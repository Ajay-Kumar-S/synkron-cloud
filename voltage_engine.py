class VoltageComponent:

    def __init__(self, name, nominal_voltage):
        self.name = name
        self.nominal_voltage = nominal_voltage
        self.input_voltage = nominal_voltage
        self.output_voltage = nominal_voltage
        self.failed = False
        self.dependencies = []

    def add_dependency(self, component):
        self.dependencies.append(component)

    def evaluate(self):

        # Input comes from dependency output
        for dep in self.dependencies:
            self.input_voltage = dep.output_voltage

        if self.failed:
            self.output_voltage = 0
        else:
            self.output_voltage = self.input_voltage


def build_voltage_system():

    power = VoltageComponent("Power Supply", 230)
    safety = VoltageComponent("Safety Chain", 230)
    controller = VoltageComponent("Controller", 230)
    drive = VoltageComponent("Drive", 230)
    brake = VoltageComponent("Brake Coil", 230)
    motor = VoltageComponent("Motor", 230)

    safety.add_dependency(power)
    controller.add_dependency(safety)
    drive.add_dependency(controller)
    brake.add_dependency(drive)
    motor.add_dependency(brake)

    return {
        "power": power,
        "safety": safety,
        "controller": controller,
        "drive": drive,
        "brake": brake,
        "motor": motor
    }
