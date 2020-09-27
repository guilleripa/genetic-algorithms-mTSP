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
    swap_op,
)

random.seed(0)


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
        part_one_edit(tools.cxPartialyMatched, len(instance_dict["stores"])),
    )
    toolbox.register(
        "mutate_swap", part_one_edit(swap_op, len(instance_dict["stores"]))
    )

    inc_op_w_max = partial(inc_op, len(instance_dict["stores"]))

    toolbox.register(
        "mutate_inc", part_two_edit(inc_op_w_max, len(instance_dict["stores"]))
    )
    toolbox.register("mutate_dec", part_two_edit(dec_op, len(instance_dict["stores"])))

    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register(
        "correct_routes", correct_route, len(instance_dict["stores"]) - 1, instance_dict
    )

    return toolbox, current_instance.config, current_instance.get_store_positions()


@click.command()
@click.option("--ins", required=True)
@click.option("--h/--no-h", default=False)
@click.option("--save-fig", is_flag=True)
@click.option(
    "--part2_type",
    default="greedy",
    type=click.Choice(["uniform", "choice", "greedy"]),
)
@click.option("--cxpb1", default=0.5, type=float)
@click.option("--mutpb1", default=0.2, type=float)
@click.option("--mutpb2", default=0.2, type=float)
def main(ins, h, save_fig, part2_type, cxpb1, mutpb1, mutpb2):
    saved_args = locals()
    toolbox, config, stores = create_toolbox(
        ins, heterogeneous_vehicles=h, part2_type=part2_type
    )
    start = time.time()
    pop = toolbox.population(n=100)

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
    run_name = f"{config}_{datetime.now().strftime('%m_%d_%H%M%S')}"
    output_folder = Path("results") / run_name
    output_folder.mkdir()
    with open(output_folder / f"config.txt", "w+") as f_config:
        for arg in saved_args:
            f_config.write(f"{arg}={saved_args[arg]}\n")

    # Extracting all the fitnesses of
    fits = [ind.fitness.values[0] for ind in pop]

    # Begin the evolution
    for g in tqdm(range(1000)):
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

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
            if mutated:
                toolbox.correct_routes(mutant)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5

        output.append(f"{g}, {min(fits):.5f}, {max(fits):.5f}, {mean:.5f}, {std:.5f}\n")
        # Plot the fittest every 100 generations
        if (g + 1) % 100 == 0 or g == 0:
            fraser = pop[np.argmin(fits)]
            draw_individual(fraser, stores, g, run_name, save_fig=save_fig)

    elapsed = time.time() - start
    elapsed = f"Algorithm took {elapsed:.2f}s\n\n"
    with open(output_folder / f"config.txt", "w") as f_config:
        f_config.write(elapsed)
    with open(output_folder / f"fitness.csv", "w+") as f_fitnesses:
        f_fitnesses.write("g, min, max, mean, std\n")
        f_fitnesses.writelines(output)


if __name__ == "__main__":
    main(["--ins", "C101"])
