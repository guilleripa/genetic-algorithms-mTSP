import logging
import math
import random

import matplotlib.pyplot as plt
import numpy as np

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


def init_iterate_and_distribute(container, instance=None):
    if not instance:
        raise ValueError("`instance` cannot be None.")

    store_count, vehicle_count = len(instance["stores"]) - 1, len(instance["vehicles"])

    # routes
    individual = random.sample(range(1, store_count + 1), store_count)
    # route assignment
    individual.extend(sorted(random.choices(range(store_count), k=vehicle_count - 1)))

    assert validate_capacities(
        individual, store_count, instance
    ), "A vehicle has more demand than capacity."
    return container(individual)


#
# Wrappers to make operators work only on one part of the genome.
#


def part_one_edit(func, part_one_len):
    def apply_part_one(*args):
        part1 = slice(part_one_len)
        parts = [ind[part1] for ind in args]
        for updated, original in zip(func(*parts), args):
            original[part1] = updated
        return args

    return apply_part_one


def part_two_edit(func, part_one_len):
    def apply_part_two(*args):
        part2 = slice(part_one_len, None)
        parts = [ind[part2] for ind in args]
        for updated, original in zip(func(*parts), args):
            original[part2] = updated
        return args

    return apply_part_two


#
# Mutation operators
#


def swap_op(ind):
    # Swap two genes of the individual.
    idx1 = random.randint(0, len(ind) - 1)
    idx2 = random.randint(0, len(ind) - 1)
    ind[idx1], ind[idx2] = ind[idx2], ind[idx1]
    return (ind,)


def inc_op(max_value, ind):
    # Sums one to a gene and substracts one to other.
    inc_idx = random.randint(0, len(ind) - 1)

    if ind[inc_idx] + 1 <= max_value and (
        inc_idx == len(ind) - 1 or ind[inc_idx] < ind[inc_idx + 1]
    ):
        ind[inc_idx] += 1
    return (ind,)


def dec_op(ind):
    # Sums one to a gene and substracts one to other.
    dec_idx = random.randint(0, len(ind) - 1)
    if ind[dec_idx] - 1 >= 0 and (dec_idx == 0 or ind[dec_idx - 1] <= ind[dec_idx]):
        ind[dec_idx] -= 1
    return (ind,)


def regenerate_op(ind, max_value):
    ind_len = len(ind)
    ind = random.sample(range(max_value), ind_len)
    ind.sort()
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

    # Add return to deposit time
    t += calculate_distance(*prev_store["position"], *instance["stores"][0]["position"])
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


#
# Drawing tools
#


def draw_individual(ind, stores):
    num_stores = len(stores)
    fig, ax = plt.subplots(2, sharex=True, sharey=True)  # Prepare 2 plots
    ax[0].set_title("Raw nodes")
    ax[1].set_title("Optimized tours")
    start = 0
    for i, finish in enumerate(np.append(ind[num_stores:], num_stores)):
        ind_slice = ind[start:finish]
        store_slice = stores[ind_slice]
        res = ax[0].scatter(store_slice[:, 0], store_slice[:, 1])  # plot A
        ax[1].scatter(store_slice[:, 0], store_slice[:, 1])  # plot B
        for j in range(len(ind_slice)):
            start_node = ind_slice[j]
            start_pos = stores[start_node]
            next_node = ind_slice[(j + 1) % len(ind_slice)]
            end_pos = stores[next_node]
            ax[1].annotate(
                "",
                xy=start_pos,
                xycoords="data",
                xytext=end_pos,
                textcoords="data",
                arrowprops=dict(
                    arrowstyle="->",
                    connectionstyle="arc3",
                    color=res.get_facecolors()[0],
                ),
            )
        start = finish

    plt.tight_layout()
    plt.show()
