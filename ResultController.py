from ConfigController import *

import matplotlib.pyplot as plt

from typing import List

from Tests.IJMeterTest import IJMeterTest, PlotOptions
from Tests.Provider import Provider

plt.rcParams.update({"font.size": 14})
plt.rcParams["font.family"] = "Arial"

colors = [
    "red",
    "green",
    "blue",
    "orange",
    "yellow",
    "pink",
    "grey",
    "brown",
    "olive",
    "cyan",
    "purple",
    "darksalmon",
    "lime",
    "dodgerblue",
    "springgreen",
    "hotpink",
]


def plot_result(
    jmeter_test: IJMeterTest,
    files: List,
    ts: float,
    providers: List[Provider],
    execution_time: str,
):
    result_path = benchmark_result_path(jmeter_test.get_test_name())
    result_name = "multiple" if len(providers) != 1 else providers[0]
    jmeter_test.plot(PlotOptions(files, execution_time, colors, result_path, result_name, ts))


def benchmark_result_path(test_number):
    config = read_conf()
    return str(config["benchmarkResultsPath"][test_number])
