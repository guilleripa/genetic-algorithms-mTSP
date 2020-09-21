import logging
import math
import random

logger = logging.getLogger("Toolbox")

#
# mTSP specific initializer
#


def valid_route_capacity(route, vehicle_idx, instance):
    """
    Given a route and a vehicle we check that the vehicle can fulfill the route's demand.
    """
    max_demand = instance["vehicles"][vehicle_idx]["capacity"]
    route_demand = 0
    for store in route:
        route_demand += instance["stores"][store]["demand"]
        if route_demand > max_demand:
            return False
    return True


def validate_capacities(individual, store_count, instance):
    # TODO: si vemos que falla en alguna implementamos esto:
    # Queremos recorrer al individuo e ir llevando la carga total de cada vehículo.
    # Si vemos que alcanza, está todo bien y seguimos, sino, cortamos ahí y le pasamos las tiendas restantes al siguiente camión.
    # Si el último camión tiene tiendas sobrantes, entonces movemos la parte 1 para darle esas al primer camión y volvermos a arrancar.

    routes, route_idxs = individual[:store_count], individual[store_count:]
    route_start_idx = 0
    for vehicle_idx, route_finish_idx in enumerate(route_idxs + [store_count]):
        if not valid_route_capacity(
            routes[route_start_idx:route_finish_idx], vehicle_idx, instance
        ):
            return False
        route_start_idx += route_finish_idx
    return True


def init_iterate_and_distribute(container, instance):
    store_count, vehicle_count = len(instance["stores"]) - 1, len(instance["vehicles"])

    # routes
    individual = random.sample(range(store_count), store_count)
    # route assignment
    individual.extend(sorted(random.choices(range(store_count), k=vehicle_count - 1)))

    assert validate_capacities(individual, store_count, instance)
    return container(individual)


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


#
# Evaluation function
#


def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def eval_route(route, v_idx, instance):
    t = cost = 0

    prev_store = instance["stores"][0]
    for store_idx in route:
        store = instance["stores"][store_idx]
        t += calculate_distance(*prev_store["position"], *store["position"])

        ready_time, due_date = store["window"]
        if t < ready_time:
            t = ready_time
        t += store["service_time"]
        cost += abs(t - due_date)

        prev_store = store

    return cost + t * instance["vehicles"][v_idx]["rate"]


def eval_routes(individual, instance=None):
    if not instance:
        raise ValueError("`instance` cannot be None.")

    store_count = len(instance["stores"]) - 1
    routes, route_idxs = individual[:store_count], individual[store_count:]

    cost = 0
    route_start_idx = 0
    for v_idx, route_finish_idx in enumerate(route_idxs + [store_count]):
        cost += eval_route(routes[route_start_idx:route_finish_idx], v_idx, instance)
        route_start_idx = route_finish_idx

    return (cost,)
