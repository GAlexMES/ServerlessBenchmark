from ConfigController import *

import matplotlib.pyplot as plt

from typing import List

from Tests.IJMeterTest import IJMeterTest, PlotOptions, Result
from Tests.Provider import Provider

plt.rcParams.update({"font.size": 14})
plt.rcParams["font.family"] = "Arial"


def plot_result(
    jmeter_test: IJMeterTest,
    results: List[Result],
    ts: int,
    providers: List[Provider],
    execution_time: str,
):
    result_path = benchmark_result_path(jmeter_test.get_test_name())
    jmeter_test.plot(PlotOptions(results, execution_time, result_path, providers, ts))


def benchmark_result_path(test: str) -> str:
    config = read_conf()
    return "{0}/{1}".format(str(config["benchmarkResultsPath"]), test)
