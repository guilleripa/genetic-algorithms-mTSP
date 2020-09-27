import random
import time
from datetime import datetime
from functools import partial
from pathlib import Path

import click
import numpy as np
from deap import base, creator, tools
from instances.parser import Instancer
from tqdm import tqdm

from scripts.utils import (
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


def create_toolbox(instance_type, heterogeneous_vehicles):
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
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval_routes, instance=instance_dict)
    # # TODO: add cx fns.
    toolbox.register(
        "mate_1", part_one_edit(tools.cxPartialyMatched, len(instance_dict["stores"]))
    )
    # # TODO: add mutation fns.
    # toolbox.register("mutate_1", tools.mutFlipBit, indpb=0.05)
    toolbox.register(
        "mutate_swap", part_one_edit(swap_op, len(instance_dict["stores"]))
    )

    inc_op_w_max = partial(inc_op, len(instance_dict["stores"]))

    toolbox.register(
        "mutate_inc", part_two_edit(inc_op_w_max, len(instance_dict["stores"]))
    )
    toolbox.register("mutate_dec", part_two_edit(dec_op, len(instance_dict["stores"])))

    toolbox.register("select", tools.selTournament, tournsize=3)

    return toolbox, current_instance.config, current_instance.get_store_positions()


@click.command()
@click.option("--ins", required=True)
@click.option("--h/--no-h", default=False)
@click.option("--save-fig", is_flag=True)
def main(ins, h, save_fig):
    toolbox, config, stores = create_toolbox(ins, heterogeneous_vehicles=h)
    start = time.time()
    pop = toolbox.population(n=100)

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # CXPB1  is the probability with which part 1 of two individuals
    #        are crossed
    #
    # MUTPB1 is the probability for mutating part 1 of an individual
    # MUTPB2 is the probability for mutating part 2 of an individual
    output = []
    run_name = f"{config}_{datetime.now().strftime('%m_%d_%H%M%S')}"
    output_folder = Path("results") / run_name
    output_folder.mkdir()
    with open(output_folder / f"{run_name}.txt", "w+") as f:
        CXPB1, MUTPB1, MUTPB2 = 0.5, 0.2, 0.2
        f.write(
            f"instance={config}, CXPB1={CXPB1}, MUTPB1={MUTPB1}, MUTPB2={MUTPB2} \n"
        )
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
                if random.random() < CXPB1:
                    toolbox.mate_1(child1, child2)
                    if hasattr(child1.fitness, "values"):
                        del child1.fitness.values
                    if hasattr(child2.fitness, "values"):
                        del child2.fitness.values

            for mutant in offspring:
                if random.random() < MUTPB1:
                    toolbox.mutate_swap(mutant)
                    if hasattr(mutant.fitness, "values"):
                        del mutant.fitness.values
                if random.random() < MUTPB2:
                    toolbox.mutate_inc(mutant)
                    if hasattr(mutant.fitness, "values"):
                        del mutant.fitness.values
                if random.random() < MUTPB2:
                    toolbox.mutate_dec(mutant)
                    if hasattr(mutant.fitness, "values"):
                        del mutant.fitness.values

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
            if g % 99 == 0:
                fraser = pop[np.argmax(fits)]
                draw_individual(fraser, stores, g, run_name, save_fig=save_fig)

        elapsed = time.time() - start
        elapsed = f"Algorithm took {elapsed:.2f}s\n\n"
        f.write(elapsed)
        f.write("min, max, mean, std\n")
        f.writelines(output)


if __name__ == "__main__":
    main(["--ins", "C101"])
