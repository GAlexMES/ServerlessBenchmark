import os

import matplotlib.pyplot as plt
import xml.etree.ElementTree as ElementTree

from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import save_fig, plot_real_latency
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
)


class OverheadTest(IJMeterTest):

    jmeter_template = os.path.join(os.path.dirname(__file__), "Overhead.jmx")

    def get_test_name(self):
        return "T01OverheadTest"

    def run(self, options: RunOptions) -> str or None:
        execution_time = options.args[2]

        template = ElementTree.ElementTree(file=self.jmeter_template)

        update_t1_template(options.function_url, execution_time, template, self.jmeter_template)
        file_name = get_output_file_name(options.ts, options.provider.value)

        run_jmeter(file_name, self.get_test_name(), options.provider.value, self.jmeter_template)
        # print(str(jmeter_result.decode('UTF-8')))

        file = (file_name, options.provider.value)
        options.files.append(file)

        return execution_time

    def plot(self, options: PlotOptions):
        color_n = 0
        ax = plt.gca()
        for file in options.files:
            provider = file[1]
            if provider == "ow":
                provider = "ibm bluemix"

            print(
                "\n\n\n Result for test T {0} in the {1} provider during {2} seconds:".format(
                    self.get_test_name(), provider, options.execution_time
                )
            )
            plot_real_latency(options.colors[color_n], provider, ax, self.get_test_name(), str(file[0]))
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title("Latency of a sequence of invocations during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider.value, options.ts)
