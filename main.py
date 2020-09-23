import random
from functools import partial

from deap import base, creator, tools

from instances.parser import Instancer
from utils import (
    dec_op,
    eval_routes,
    inc_op,
    init_iterate_and_distribute,
    part_one_edit,
    part_two_edit,
    regenerate_op,
    swap_op,
)

random.seed(0)

current_instance = Instancer("C109").get_instance_dict()

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Structure initializers
toolbox.register(
    "individual",
    init_iterate_and_distribute,
    creator.Individual,
    instance=current_instance,
)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", eval_routes, instance=current_instance)
# # TODO: add cx fns.
toolbox.register("mate_1", part_one_edit(tools.cxPartialyMatched, len(current_instance["stores"])))
# # TODO: add mutation fns.
# toolbox.register("mutate_1", tools.mutFlipBit, indpb=0.05)
toolbox.register("mutate_swap", part_one_edit(swap_op, len(current_instance["stores"])))

inc_op_w_max = partial(inc_op, len(current_instance["stores"]))

toolbox.register("mutate_inc", part_two_edit(inc_op_w_max))
toolbox.register("mutate_dec", part_two_edit(dec_op))

toolbox.register("select", tools.selTournament, tournsize=3)


def main():
    pop = toolbox.population(n=100)

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # CXPB1  is the probability with which part 1 of two individuals
    #        are crossed
    # CXPB2  is the probability with which part 2 of two individuals
    #        are crossed
    #
    # MUTPB1 is the probability for mutating part 1 of an individual
    # MUTPB2 is the probability for mutating part 2 of an individual
    CXPB1, MUTPB1, MUTPB2 = 0.5, 0.2, 0.2

    # Extracting all the fitnesses of
    fits = [ind.fitness.values[0] for ind in pop]
    # Variable keeping track of the number of generations
    g = 0

    # Begin the evolution
    while g < 1000:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)

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

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)


if __name__ == "__main__":
    main()
