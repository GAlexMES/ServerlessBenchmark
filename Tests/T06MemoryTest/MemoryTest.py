import os

import matplotlib.pyplot as plt

from Colors import colors
from Tests.IJMeterTest import PlotOptions, IProviderSpecificJMeterTest
from Tests.PlotHelper import save_fig, plot_real_latency
from Tests.Provider import Provider


class MemoryTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Memory.jmx")
    info_message_format = "No function with {0}Mb of memory for test {1} on {2} provider"
    supported_providers = [Provider.aws, Provider.ow, Provider.google]
    options = {
        Provider.aws: ["M128", "M256", "M512", "M1024", "M2048"],
        Provider.google: ["M128", "M256", "M512", "M1024", "M2048"],
        Provider.ow: ["M128", "M256", "M384", "M512"],
    }

    def get_test_name(self):
        return "T06MemoryTest"

    def plot(self, options: PlotOptions):
        color_n = 0
        for result in options.results:
            memory = result.option
            print(
                "\n\n\nResult for test T {0} in the {1} provider during {2} seconds, with {3} of memory of function:".format(
                    self.get_test_name(),
                    result.provider_name,
                    options.execution_time,
                    memory,
                )
            )
            plot_real_latency(colors[color_n], memory, self.get_test_name(), result.file_name)
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations with different memory levels during {0} seconds".format(
                options.execution_time
            )
        )

        save_fig(plt, options.result_path, options.provider, options.ts)
