import os

import matplotlib.pyplot as plt
import xml.etree.ElementTree as ElementTree

from ResultController import Result
from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import save_fig, plot_real_latency
from Tests.Provider import Provider
from Tests.TestHelpers import (
    update_t1_template,
    run_jmeter,
)


class OverheadTest(IJMeterTest):

    jmeter_template = os.path.join(os.path.dirname(__file__), "Overhead.jmx")

    def get_test_name(self):
        return "T01OverheadTest"

    def get_function_path(self, provider: Provider) -> str:
        return "../ServerlessFunctions/SimpleGetEndpoints/{0}GetEndpoint".format(provider.value)

    def run(self, options: RunOptions):
        template = ElementTree.ElementTree(file=self.jmeter_template)

        update_t1_template(options.function_url, options.execution_time, template, self.jmeter_template)
        file_name = self.get_output_file_name(options.ts, options.provider)

        run_jmeter(file_name, self.get_test_name(), options.provider.value, self.jmeter_template)

        options.results.append(Result(file_name, options.provider.value))

    def plot(self, options: PlotOptions):
        color_n = 0
        for result in options.results:
            provider = result.provider_name
            if provider == "ow":
                provider = "ibm bluemix"

            print(
                "\n\n\n Result for test T {0} in the {1} provider during {2} seconds:".format(
                    self.get_test_name(), provider, options.execution_time
                )
            )
            plot_real_latency(options.colors[color_n], provider, self.get_test_name(), result.file_name)
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title("Latency of a sequence of invocations during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider, options.ts)
