import random

import numpy as np


def initIterateAndDistribute(container, store_count, vehicle_count):
    vehicle_routes = random.sample(range(store_count), store_count)

    # The store_count will be the total sum to keep, then we distribute it between vehicles.
    # Finally we remove the last one to keep solution consistency.
    vehicle_assignment_counts = np.random.multinomial(
        store_count, np.ones(vehicle_count) / vehicle_count, size=1
    )[0][:-1]

    vehicle_routes.extend(vehicle_assignment_counts)

    return container(vehicle_routes)
