from fault_database import FAULT_TREE

active_cases = []
current_nodes = {}


def start_diagnosis(issue_key):

    global active_cases, current_nodes

    if issue_key not in FAULT_TREE:
        return "Diagnostic tree not available."

    if issue_key not in active_cases:
        active_cases.append(issue_key)
        current_nodes[issue_key] = FAULT_TREE[issue_key]

    return FAULT_TREE[issue_key]["initial_question"]


def process_answer(answer):

    global active_cases, current_nodes

    answer = answer.lower().strip()

    if answer not in ["yes", "no"]:
        return "Please answer with 'yes' or 'no'."

    responses = []

    for case in active_cases:

        node = current_nodes.get(case)

        if not node:
            continue

        if answer not in node:
            continue

        next_node = node[answer]

        if "result" in next_node:
            responses.append(
                f"[{case.upper()}]\nRoot Cause:\n{next_node['result']}"
            )
            current_nodes[case] = None
        else:
            current_nodes[case] = next_node
            responses.append(next_node["question"])

    if not responses:
        return "No valid diagnostic path."

    return "\n\n".join(responses)


def correlate_active_cases():

    if len(active_cases) < 2:
        return None

    correlation_message = (
        "Multiple fault modules active.\n"
        "Cross-check shared systems such as:\n"
        "- Safety chain integrity\n"
        "- Power supply stability\n"
        "- Control PCB common outputs\n"
        "- Traveling cable continuity\n"
    )

    return correlation_message
