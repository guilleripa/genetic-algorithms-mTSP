import logging
import random

import numpy as np

logger = logging.getLogger("Toolbox")


def valid_route_capacity(route, vehicle_idx, instances):
    """
    Given a route and a vehicle we check that the vehicle can fulfill the route's demand.
    """
    # we are assuming
    # instances ~= {
    # 'vehicles': [[driver_rate, vehicle_capacity]],
    # 'stores': [[..., store_demand]]
    # }
    max_capacity = instances["vehicles"][vehicle_idx][-1]
    current_capacity = 0
    for store in route:
        current_capacity += instances["stores"][store][-1]
        if current_capacity > max_capacity:
            return False
    return True


def validate_capacities(genome, store_count, instances):
    # TODO: si vemos que falla en alguna implementamos esto:
    # Queremos recorrer el genoma e ir llevando la carga total de cada vehículo.
    # Si vemos que alcanza, está todo bien y seguimos, sino, cortamos ahí y le pasamos las tiendas restantes al siguiente camión.
    # Si el último camión tiene tiendas sobrantes, entonces movemos la parte 1 para darle esas al primer camión y volvermos a arrancar.

    routes, route_counts = genome[:store_count], genome[store_count:]
    start = 0
    for vehicle_idx, route_count in enumerate(route_counts):
        # we are assuming instances ~= {'vehicles': [[driver_rate, vehicle_capacity]]}
        route = routes[start : start + route_count]
        if not valid_route_capacity(route, vehicle_idx, instances):
            return False
        start += route_count

    route = routes[start:]
    return valid_route_capacity(route, len(route_counts), instances)


def initIterateAndDistribute(container, store_count, vehicle_count, instances):
    routes = random.sample(range(store_count), store_count)

    # The store_count will be the total sum to keep, then we distribute it between vehicles.
    # Finally we remove the last one to keep solution consistency.
    route_counts = np.random.multinomial(
        store_count, np.ones(vehicle_count) / vehicle_count, size=1
    )[0][:-1]

    routes.extend(route_counts)

    assert validate_capacities(routes, store_count, instances)
    return container(routes)


#
# Wrappers to make operators work only on one part of the genome.
#


def part_one_edit(func, part_one_len):
    def apply_part_one(ind1, ind2):
        part1 = slice(part_one_len - 1)
        ind1[part1], ind2[part1] = func(ind1[part1], ind2[part1])
        return ind1, ind2

    return apply_part_one


def part_two_edit(func, part_one_len):
    def apply_part_two(ind1, ind2):
        part2 = slice(part_one_len, len(ind1))
        ind1[part2], ind2[part2] = func(ind1[part2], ind2[part2])
        return ind1, ind2

    return apply_part_two


#
# Mutation operators
#


def swap_op(ind):
    # Swap two genes of the individual.
    idx1 = random.randint(0, len(ind))
    idx2 = random.randint(0, len(ind))
    ind[idx1], ind[idx2] = ind[idx2], ind[idx1]
    return ind


def inc_dec(ind):
    # Sums one to a gene and substracts one to other.
    inc_idx = random.randint(0, len(ind))
    dec_idx = random.randint(0, len(ind))
    ind[inc_idx] += 1
    ind[dec_idx] -= 1
    return ind
