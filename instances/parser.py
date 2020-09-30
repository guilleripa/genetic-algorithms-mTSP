from pathlib import Path
from random import shuffle

import numpy as np

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
        {"count": 20, "capacity": 100, "type": "A", "rate": 1.0},
        {"count": 5, "capacity": 200, "type": "B", "rate": 1.2},
    ],
    "C2": [
        {"count": 20, "capacity": 400, "type": "A", "rate": 1.0},
        {"count": 5, "capacity": 500, "type": "B", "rate": 1.2},
    ],
    "R1": [
        {"count": 10, "capacity": 50, "type": "A", "rate": 1.0},
        {"count": 15, "capacity": 80, "type": "B", "rate": 1.2},
        {"count": 10, "capacity": 120, "type": "C", "rate": 1.4},
    ],
    "R2": [
        {"count": 10, "capacity": 300, "type": "A", "rate": 1.0},
        {"count": 5, "capacity": 400, "type": "B", "rate": 1.2},
    ],
    "RC1": [
        {"count": 10, "capacity": 40, "type": "A", "rate": 1.0},
        {"count": 20, "capacity": 80, "type": "B", "rate": 1.2},
        {"count": 10, "capacity": 150, "type": "C", "rate": 1.4},
    ],
    "RC2": [
        {"count": 10, "capacity": 100, "type": "A", "rate": 1.0},
        {"count": 5, "capacity": 200, "type": "B", "rate": 1.2},
    ],
}
PARSE_MAPPING = {1: "position", 3: "demand", 4: "window", 6: "service_time"}


class Instancer:
    def __init__(self, instance_type, heterogeneous_vehicles=False):
        instance_type = instance_type.upper()
        self.config = "H" + instance_type if heterogeneous_vehicles else instance_type
        self.stores = self.load_stores(instance_type)
        # double swichtaroo
        warehouse = self.stores.pop(0)
        self.stores.append(warehouse)
        vehicles_types = HETERO_VEHICLES if heterogeneous_vehicles else HOMO_VEHICLES
        self.vehicles = vehicles_types[instance_type[:-2]]

    def load_stores(self, instance_type):
        with open(
            Path(__file__).absolute().parent / f"{instance_type[:-2]}.txt",
            "r",
        ) as file:
            lines = file.readlines()

        stores = []
        for idx, line1 in enumerate(lines):
            if instance_type in line1:
                for line2 in lines[idx + 1 :]:
                    if instance_type[:-2] in line2:
                        break
                    line_split = line2.split()
                    try:
                        line_split = [float(value) for value in line_split]
                        store = {}
                        for idx, value in enumerate(line_split):
                            key = PARSE_MAPPING.get(idx)
                            if key:
                                store[key] = (
                                    (value, line_split[idx + 1])
                                    if idx in [1, 4]
                                    else value
                                )
                        stores.append(store) if store else None
                    except:
                        pass
                break

        return stores

    def types2list(self):
        vehicles = []
        for type in self.vehicles:
            vehicles.extend(
                [
                    {key: type[key] for key in type if key != "count"}
                    for _ in range(type["count"])
                ]
            )
        return vehicles

    def get_instance_dict(self):
        route_idx = self.types2list()
        shuffle(route_idx)
        return {"stores": self.stores, "vehicles": route_idx}

    def get_store_positions(self):
        return np.array([np.array(store["position"]) for store in self.stores])
