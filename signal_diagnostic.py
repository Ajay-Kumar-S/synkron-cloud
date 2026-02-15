from system_model import build_signal_system


def simulate_failure(user_input):

    components = build_signal_system()
    lower = user_input.lower()

    # Inject symptoms
    if "not moving" in lower:
        components["movement"].failed = True

    if "door not closing" in lower:
        components["door"].failed = True

    # Evaluate system
    for comp in components.values():
        comp.evaluate()

    return analyze_root_cause(components)


def analyze_root_cause(components):

    # Check signal break from bottom up
    if not components["movement"].output_signal:
        if not components["motor"].output_signal:
            return "Motor not receiving output signal. Investigate brake or drive stage."
        if not components["brake"].output_signal:
            return "Brake not releasing. Check brake coil voltage."
        if not components["drive"].output_signal:
            return "Drive not issuing output. Verify run command and drive status."
        if not components["controller"].output_signal:
            return "Controller not sending run signal. Check safety chain."
        if not components["safety"].output_signal:
            return "Safety chain open. Inspect door locks and safety switches."
        if not components["power"].output_signal:
            return "Main power supply interruption."

    if not components["door"].output_signal:
        return "Door system not receiving control signal. Check door controller or safety sensor."

    return "Signal path appears intact. Perform mechanical inspection."
