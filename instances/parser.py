HOMO_VEHICLES = {
    "C1": [{"count": 25, "capacity": 200, "rate": 1.0}],
    "C2": [{"count": 25, "capacity": 700, "rate": 1.0}],
    "R1": [{"count": 25, "capacity": 200, "rate": 1.0}],
    "R2": [{"count": 25, "capacity": 1000, "rate": 1.0}],
    "RC1": [{"count": 25, "capacity": 200, "rate": 1.0}],
    "RC2": [{"count": 25, "capacity": 1000, "rate": 1.0}],
}

HETERO_VEHICLES = {
    "C1": [
        {"count": 20, "capacity": 100, "rate": 1.0},
        {"count": 5, "capacity": 200, "rate": 1.2},
    ],
    "C2": [
        {"count": 20, "capacity": 400, "rate": 1.0},
        {"count": 5, "capacity": 500, "rate": 1.2},
    ],
    "R1": [
        {"count": 10, "capacity": 50, "rate": 1.0},
        {"count": 15, "capacity": 80, "rate": 1.2},
        {"count": 10, "capacity": 120, "rate": 1.4},
    ],
    "R2": [
        {"count": 10, "capacity": 300, "rate": 1.0},
        {"count": 5, "capacity": 400, "rate": 1.2},
    ],
    "RC1": [
        {"count": 10, "capacity": 40, "rate": 1.0},
        {"count": 20, "capacity": 80, "rate": 1.2},
        {"count": 10, "capacity": 150, "rate": 1.4},
    ],
    "RC2": [
        {"count": 10, "capacity": 100, "rate": 1.0},
        {"count": 5, "capacity": 200, "rate": 1.2},
    ],
}


class Instancer:
    def __init__(self, instance_type, homogeneous_vehicles=True):
        self.stores = self.load_stores(instance_type)
        vehicles_types = HOMO_VEHICLES if homogeneous_vehicles else HETERO_VEHICLES
        self.vehicles = vehicles_types[instance_type]

    def load_stores(self, instance_type):
        pass

    def types2list(self):
        pass

    def get_instance_dict(self):
        return {"stores": self.stores, "vehicles": self.types2list()}
