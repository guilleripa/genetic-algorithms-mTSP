class TwoPartCrossover:
    def __init__(self, num_trucks, num_stores, crossover_func=None):
        self.num_trucks = num_trucks
        self.num_stores = num_stores
        self.crossover_func = crossover_func

    def run(self, ind1, ind2):
        if self.crossover_func:
            part1 = slice(self.num_stores - 1)
            ind1[part1], ind2[part1] = self.crossover_func(ind1[part1], ind2[part1])
            return ind1, ind2
