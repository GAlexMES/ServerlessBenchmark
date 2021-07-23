import os
import matplotlib.pyplot as plt

from Colors import colors
from Tests.IJMeterTest import PlotOptions, IProviderSpecificJMeterTest
from Tests.PlotHelper import save_fig, plot_real_latency
from Tests.Provider import Provider


class OverheadLanguagesTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "OverheadLanguages.jmx")
    info_message_format = "No function in {0} for test {1} on {2} provider"
    options = {
        Provider.aws: ["Go", "Java", "NodeJs", "Python"],
        Provider.ow: ["NodeJs", "Php", "Python", "Ruby", "Swift"],
    }
    supported_providers = [Provider.aws, Provider.ow]

    def get_test_name(self):
        return "T05OverheadLanguagesTest"

    def plot(self, options: PlotOptions):
        color_n = 0
        for result in options.results:
            language = result.option
            print(
                "\n\n\n Result for test T {0} in the {1} provider during {2} seconds, with {3} as programming language of function:".format(
                    self.get_test_name(),
                    result.provider_name,
                    options.execution_time,
                    language,
                )
            )
            plot_real_latency(colors[color_n], language, self.get_test_name(), result.file_name)
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations of different programming languages during {0} seconds".format(
                options.execution_time
            )
        )

        save_fig(plt, options.result_path, options.provider, options.ts)
