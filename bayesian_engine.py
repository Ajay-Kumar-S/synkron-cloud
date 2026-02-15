class BayesianModel:

    def __init__(self):
        self.hypotheses = {
            "safety_chain_open": 0.3,
            "drive_fault": 0.4,
            "brake_fault": 0.2,
            "motor_fault": 0.1
        }

    def update(self, evidence):

        if "motor voltage = 0" in evidence:
            self.hypotheses["drive_fault"] += 0.2
            self.hypotheses["safety_chain_open"] -= 0.1

        if "brake voltage = 230" in evidence:
            self.hypotheses["brake_fault"] -= 0.1

        self.normalize()

    def normalize(self):
        total = sum(self.hypotheses.values())
        for key in self.hypotheses:
            self.hypotheses[key] /= total

    def get_ranked(self):
        return sorted(
            self.hypotheses.items(),
            key=lambda x: x[1],
            reverse=True
        )
