import json
import os

FILE = "failure_history.json"


def store_case(symptom, root_cause):

    data = {}

    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            data = json.load(f)

    if symptom not in data:
        data[symptom] = {}

    data[symptom][root_cause] = data[symptom].get(root_cause, 0) + 1

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_history(symptom):

    if not os.path.exists(FILE):
        return None

    with open(FILE, "r") as f:
        data = json.load(f)

    return data.get(symptom, None)
