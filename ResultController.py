from ConfigController import *

import matplotlib.pyplot as plt

from typing import List

from Tests.IJMeterTest import IJMeterTest

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
    serverless_provider: str,
    execution_time: str,
):
    result_path = benchmark_result_path(jmeter_test.get_test_name())
    jmeter_test.plot(files, execution_time, colors, result_path, serverless_provider, ts)


def benchmark_result_path(test_number):
    config = read_conf()
    return str(config["benchmarkResultsPath"][test_number])
