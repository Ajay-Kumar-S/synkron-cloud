class SignalComponent:

    def __init__(self, name):
        self.name = name
        self.input_signal = True
        self.output_signal = True
        self.failed = False
        self.dependencies = []

    def add_dependency(self, component):
        self.dependencies.append(component)

    def evaluate(self):

        # If any dependency output is False → input becomes False
        for dep in self.dependencies:
            if not dep.output_signal:
                self.input_signal = False

        # If component itself failed → no output
        if self.failed:
            self.output_signal = False
        else:
            self.output_signal = self.input_signal


def build_signal_system():

    power = SignalComponent("Power Supply")
    safety = SignalComponent("Safety Chain")
    controller = SignalComponent("Controller")
    drive = SignalComponent("Drive")
    brake = SignalComponent("Brake")
    motor = SignalComponent("Motor")
    movement = SignalComponent("Car Movement")
    door = SignalComponent("Door System")

    # Dependencies
    safety.add_dependency(power)
    controller.add_dependency(safety)
    drive.add_dependency(controller)
    brake.add_dependency(drive)
    motor.add_dependency(brake)
    movement.add_dependency(motor)
    door.add_dependency(controller)

    components = {
        "power": power,
        "safety": safety,
        "controller": controller,
        "drive": drive,
        "brake": brake,
        "motor": motor,
        "movement": movement,
        "door": door
    }

    return components
