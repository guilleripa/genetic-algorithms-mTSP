# %%
import random

import numpy as np
from deap.tools import cxPartialyMatched

from utils import dec_op, inc_op, part_one_edit, regenerate_op, swap_op

# %%
swap_part_one = part_one_edit(swap_op, 6)
# %%
a = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
b = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
# random.shuffle(a)
# random.shuffle(b)
# %%
swap_part_one(a)

# %%
def test(lg, sd):
    return lg, sd


pm_one = part_one_edit(cxPartialyMatched, 10)


# %%
pm_one(a, b)

# %%
inc_op(a, 9)
# %%
regenerate_op(a, 15)
# %%
