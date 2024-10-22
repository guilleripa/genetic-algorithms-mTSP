import random
import time
from datetime import datetime
from functools import partial
from pathlib import Path

import click
import numpy as np
from deap import base, creator, tools
from tqdm import tqdm

from instances.parser import Instancer
from scripts.utils import (
    correct_route,
    dec_op,
    draw_individual,
    eval_routes,
    inc_op,
    init_iterate_and_distribute,
    part_one_edit,
    part_two_edit,
    regenerate_op,
    reverse_op,
    selInverseRoulette,
    swap_op,
)


def create_toolbox(instance_type, heterogeneous_vehicles, part2_type="greedy"):
    current_instance = Instancer(
        instance_type, heterogeneous_vehicles=heterogeneous_vehicles
    )
    instance_dict = current_instance.get_instance_dict()

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    # Structure initializers
    toolbox.register(
        "individual",
        init_iterate_and_distribute,
        creator.Individual,
        instance=instance_dict,
        part2_type=part2_type,
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval_routes, instance=instance_dict)
    toolbox.register(
        "mate_1",
        part_one_edit(tools.cxPartialyMatched, len(instance_dict["stores"]) - 1),
    )
    # toolbox.register(
    #     "mate_1",
    #     part_one_edit(tools.cxOrdered, len(instance_dict["stores"]) -1),
    # )

    toolbox.register(
        "mutate_swap", part_one_edit(swap_op, len(instance_dict["stores"]) - 1)
    )
    toolbox.register(
        "mutate_reverse", part_one_edit(reverse_op, len(instance_dict["stores"]) - 1)
    )

    inc_op_w_max = partial(inc_op, len(instance_dict["stores"]) - 1)
    toolbox.register(
        "mutate_inc", part_two_edit(inc_op_w_max, len(instance_dict["stores"]) - 1)
    )

    regen_op_w_max = partial(regenerate_op, len(instance_dict["stores"]) - 1)
    toolbox.register(
        "mutate_regen", part_two_edit(regen_op_w_max, len(instance_dict["stores"]) - 1)
    )

    toolbox.register(
        "mutate_dec", part_two_edit(dec_op, len(instance_dict["stores"]) - 1)
    )

    toolbox.register("select", tools.selTournament, tournsize=20)
    # toolbox.register("select", selInverseRoulette)
    toolbox.register(
        "correct_routes", correct_route, len(instance_dict["stores"]) - 1, instance_dict
    )

    return toolbox, current_instance


@click.command()
@click.option("--ins", default="rc101")
@click.option("--h/--no-h", default=False)
@click.option("--save-fig", is_flag=True)
@click.option("--fig-interval", default=200, type=int)
@click.option(
    "--part2-type",
    default="choice",
    type=click.Choice(["uniform", "choice", "greedy"]),
)
@click.option("--cxpb1", default=0.6, type=float)
@click.option("--mutpb1", default=0.2, type=float)
@click.option("--mutpb2", default=0.2, type=float)
@click.option("--rounds", default=1000, type=int)
@click.option("--keep-parents", is_flag=True)
@click.option("--pop-size", default=100, type=int)
@click.option("--run-name", default=None, type=str)
def main(
    ins,
    h,
    save_fig,
    fig_interval,
    part2_type,
    cxpb1,
    mutpb1,
    mutpb2,
    rounds,
    keep_parents,
    pop_size,
    run_name,
):
    saved_args = locals()
    toolbox, instance = create_toolbox(
        ins, heterogeneous_vehicles=h, part2_type=part2_type
    )
    stores = instance.get_store_positions()
    start = time.time()
    pop = toolbox.population(n=pop_size)

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # cxpb1  is the probability with which part 1 of two individuals
    #        are crossed
    #
    # MUTPB1 is the probability for mutating part 1 of an individual
    # MUTPB2 is the probability for mutating part 2 of an individual
    output = []
    if run_name is None:
        run_name = f"{instance.config}_{datetime.now().strftime('%m_%d_%H%M%S')}"
    output_folder = Path("results") / run_name
    output_folder.mkdir()
    (output_folder / "analysis").mkdir()
    with open(output_folder / "analysis" / "config.txt", "w+") as f_config:
        for arg in saved_args:
            f_config.write(f"{arg}={saved_args[arg]}\n")

    # Extracting all the fitnesses of
    fits = [ind.fitness.values[0] for ind in pop]
    all_time_fittest = pop[np.argmin(fits)]

    # Begin the evolution
    for g in tqdm(range(rounds)):
        # Select the next generation individuals
        pop = toolbox.select(pop, pop_size - 1)
        # Add back the current fittest
        pop.append(all_time_fittest)

        # Clone the selected individuals
        offspring = list(map(toolbox.clone, pop))

        # # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb1:
                toolbox.mate_1(child1, child2)
                toolbox.correct_routes(child1)
                toolbox.correct_routes(child2)
                if hasattr(child1.fitness, "values"):
                    del child1.fitness.values
                if hasattr(child2.fitness, "values"):
                    del child2.fitness.values

        for mutant in offspring:
            mutated = False

            if random.random() < mutpb1:
                mutated = True
                toolbox.mutate_swap(mutant)
                if hasattr(mutant.fitness, "values"):
                    del mutant.fitness.values
            # if random.random() < mutpb1:
            #     mutated = True
            #     toolbox.mutate_reverse(mutant)
            #     if hasattr(mutant.fitness, "values"):
            #         del mutant.fitness.values

            if random.random() < mutpb2:
                mutated = True
                toolbox.mutate_inc(mutant)
                if hasattr(mutant.fitness, "values"):
                    del mutant.fitness.values
            if random.random() < mutpb2:
                mutated = True
                toolbox.mutate_dec(mutant)
                if hasattr(mutant.fitness, "values"):
                    del mutant.fitness.values
            # if random.random() < mutpb2:
            #     mutated = True
            #     toolbox.mutate_regen(mutant)
            #     if hasattr(mutant.fitness, "values"):
            #         del mutant.fitness.values
            if mutated:
                toolbox.correct_routes(mutant)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring + pop if keep_parents else offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        # Find if we have a new fittest
        fraser = pop[np.argmin(fits)]
        if fraser.fitness.values[0] < all_time_fittest.fitness.values[0]:
            all_time_fittest = fraser

        output.append(
            f'{g},{min(fits):.5f},{max(fits):.5f},{mean:.5f},{std:.5f},"{fraser}"\n'
        )

        # Plot the fittest every 100 generations
        if (g + 1) % fig_interval == 0 or g == 0:
            draw_individual(all_time_fittest, stores, g, run_name, save_fig=save_fig)

    elapsed = time.time() - start
    elapsed = f"elapsed={elapsed:.2f}s\n"
    with open(output_folder / "analysis" / "config.txt", "a") as f_config:
        f_config.write(elapsed)
    with open(output_folder / "analysis" / "fitness.csv", "w+") as f_fitnesses:
        f_fitnesses.write("g,min,max,mean,std,ind\n")
        f_fitnesses.writelines(output)
    # Print output
    with open(output_folder / "result.txt", "w+") as f_result:
        store_count = len(stores) - 1
        routes, route_idxs = (
            all_time_fittest[:store_count],
            all_time_fittest[store_count:],
        )
        route_start_idx = 0
        vehicle_types = []
        for v_idx, route_finish_idx in enumerate(route_idxs + [store_count]):
            route = routes[route_start_idx:route_finish_idx]
            f_result.write("0 ")
            f_result.write(" ".join(str(idx) for idx in route))
            f_result.write(" 0 ")
            route_start_idx = route_finish_idx
            vehicle_types.append(
                instance.get_instance_dict()["vehicles"][v_idx]["type"]
            ) if h else None
        f_result.write("\n" + " ".join(vehicle_types) + "\n")
        f_result.write(str(all_time_fittest.fitness.values[0]))
        f_result.write("\n")


if __name__ == "__main__":
    # This values only take place when debugging
    main(["--ins", "C101", "--h", "--save-fig"])
