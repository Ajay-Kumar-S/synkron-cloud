def apply_measurement(components, measurement_text):

    parts = measurement_text.lower().split("=")

    if len(parts) != 2:
        return "Invalid measurement format. Use: component = value"

    comp_name = parts[0].strip()
    value = float(parts[1].strip())

    for comp in components.values():
        if comp.name.lower().startswith(comp_name):
            comp.output_voltage = value
            return f"{comp.name} voltage updated to {value}V"

    return "Component not found."
