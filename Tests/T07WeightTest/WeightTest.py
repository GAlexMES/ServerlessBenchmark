import os
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd

from Tests.IJMeterTest import PlotOptions, RunOptions, IProviderSpecificJMeterTest
from Tests.PlotHelper import print_result_infos, save_fig
from Tests.Provider import Provider
from Tests.TestHelpers import (
    append_query_parameter,
    get_jmeter_result_path,
)


class WeightTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Weight.jmx")

    def get_test_name(self):
        return "T07WeightTest"

    weights = ["0", "5", "10", "15", "20", "25", "30", "35", "40"]

    options = {Provider.aws: weights, Provider.google: weights, Provider.ow: weights, Provider.azure: weights}

    def run(self, options: RunOptions) -> str or None:
        url_dict: Dict[str, str] = dict()
        for weight in self.options[options.provider]:
            url_dict[weight] = append_query_parameter(options.function_url, weight)

        options.function_url = url_dict
        return super().run(options)

    def plot(self, options: PlotOptions):
        ax = plt.gca()
        color_n = 0
        for result in options.results:
            data = []
            provider = result.provider_name
            weight = result.option

            print(
                "\n\nResult for test T {0} in the {1} provider with N of Fibonacci = {2}:".format(
                    self.get_test_name(), provider, str(weight)
                )
            )

            jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + result.file_name
            df = pd.read_csv(jmeter_file)

            print_result_infos(df)
            data.append({"n_of_fib": weight, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)

            if provider == "ow":
                provider = "ibm bluemix"
            data_frame.reset_index().plot(
                marker="o",
                kind="line",
                y="avg",
                x="n_of_fib",
                color=options.colors[color_n],
                label=provider,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("N of sequence of fibonacci ")
        plt.ylabel("Latency (ms)")
        plt.title("Average latency for Fibonacci recursive during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider, options.ts)
