#%%
from random import randint

import matplotlib.pyplot as plt
import numpy as np
from numpy import random

from research.research_setup import start_plots, start_research
from utils import draw_individual

#%%
start_research()
start_plots()

# %%
num_stores = 10
stores = random.randint(0, 100, (num_stores, 2))
ind = np.array(range(10))
random.shuffle(ind)
ind = np.append(ind, random.randint(0, num_stores - 1))
# %%
fig, ax = plt.subplots(2, sharex=True, sharey=True)  # Prepare 2 plots
ax[0].set_title("Raw nodes")
ax[1].set_title("Optimized tours")
for i in range(len(ind) - num_stores + 1):
    ind_slice = ind[
        0
        if i == 0
        else ind[num_stores + i - 1] : ind[num_stores + i]
        if num_stores + i < len(ind)
        else num_stores
    ]
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
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color=res.get_facecolors()[0]),
        )

plt.tight_layout()
plt.show()


# %%
draw_individual(ind, stores)

# %%
