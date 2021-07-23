import os
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd

from Colors import colors
from Tests.IJMeterTest import IProviderSpecificJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig, plot_data_frame
from Tests.Provider import Provider
from Tests.TestHelpers import (
    append_query_parameter,
    get_jmeter_result_path,
)


class PayloadTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Payload.jmx")

    payload_sizes = ["0", "32", "64", "96", "128", "160", "192", "224", "256"]

    options = {
        Provider.aws: payload_sizes,
        Provider.google: payload_sizes,
        Provider.ow: payload_sizes,
        Provider.azure: payload_sizes,
    }

    def get_test_name(self):
        return "T04PayloadTest"

    def run(self, options: RunOptions) -> str or None:
        url_dict: Dict[str, str] = dict()
        for pay_size in self.payload_sizes:
            url_dict[pay_size] = append_query_parameter(options.function_url, pay_size)

        options.function_url = url_dict
        return super().run(options)

    def plot(self, options: PlotOptions):
        ax = plt.gca()
        color_n = 0
        for result in options.results:
            data = []

            provider = result.provider_name
            payload_size = result.option

            print("\n\n")

            print(
                "Result for test T {0} in the {1} provider with payload size = {2} kb".format(
                    self.get_test_name(), provider, str(payload_size)
                )
            )
            jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + result.file_name
            df = pd.read_csv(jmeter_file)

            print_result_infos(df)
            data.append({"payloadsize": payload_size, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)
            if provider == "ow":
                provider = "ibm bluemix"
            plot_data_frame(data_frame, "avg", "payloadsize", colors[color_n], provider, ax)
            color_n += 1

        plt.xlabel("Payload Size (KBytes)")
        plt.ylabel("Latency (ms)")
        plt.title("Average latency for payload size during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider, options.ts)
