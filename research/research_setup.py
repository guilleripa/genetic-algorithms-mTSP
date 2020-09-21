import os
import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def start_research(log_level="DEBUG"):
    os.environ["LOG_LEVEL"] = log_level

    try:
        os.chdir(os.path.join(os.getcwd(), "research"))
        print("Working on directory:", os.getcwd())
    except Exception:
        pass

    try:
        get_ipython().run_line_magic("load_ext", "autoreload")  # noqa
        get_ipython().run_line_magic("autoreload", "2")  # noqa

        print("Loaded extensions")
    except Exception:
        pass

    warnings.filterwarnings("ignore")
    print("Disabled warnings")

    np.set_printoptions(suppress=True)
    print("Set up Pandas and Numpy")


def start_plots(dpi=200):
    try:
        get_ipython().run_line_magic("config", 'InlineBackend.figure_format = "jpeg"')  # noqa
        get_ipython().run_line_magic("matplotlib", "inline")  # noqa
    except Exception:
        pass

    plt.style.use("default")
    if dpi:
        matplotlib.rcParams["figure.dpi"] = dpi
    print("Set up matplotlib")
