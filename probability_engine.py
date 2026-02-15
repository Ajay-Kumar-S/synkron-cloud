def assign_failure(component, confidence=0.7):

    component.status = "failed"
    component.confidence = confidence


def propagate_failures(components):

    for component in components.values():
        component.evaluate()


def generate_fault_report(components):

    report = []

    for comp in components.values():
        if comp.status in ["failed", "affected"]:
            report.append(
                f"{comp.name} → {comp.status} "
                f"(confidence: {comp.confidence})"
            )

    if not report:
        return "No systemic failures detected."

    return "\n".join(report)
