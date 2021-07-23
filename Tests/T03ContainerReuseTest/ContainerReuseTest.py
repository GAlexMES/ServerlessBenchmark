import os
import xml.etree.ElementTree as ElementTree
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import time

from Colors import colors
from ResultController import Result
from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig, plot_data_frame
from Tests.Provider import Provider
from Tests.TestHelpers import run_jmeter, get_function_url, get_jmeter_result_path


class ContainerReuseTest(IJMeterTest):
    jmeter_template_0 = os.path.join(os.path.dirname(__file__), "ContainerReuse_0.jmx")
    jmeter_template_1 = os.path.join(os.path.dirname(__file__), "ContainerReuse_1.jmx")

    required_arguments_count = 3
    wait_time_range = range(0, 1)

    def get_test_name(self):
        return "T03ContainerReuseTest"

    def get_function_path(self, provider: Provider) -> str:
        return "../ServerlessFunctions/SimpleGetEndpoints/{0}GetEndpoint".format(provider.value)

    def set_arguments(self, options: List[str] or None) -> bool:
        if super().check_arguments(options):
            self.wait_time_range = range(int(options[0]), int(options[1]) + 1, int(options[2]))
            return True
        return False

    def generate_result_sets(self, timestamp: int, providers: List[Provider]) -> List[Result]:
        files = []
        for provider in providers:
            for wait_time in self.wait_time_range:
                files.append(
                    Result(
                        self.get_output_file_name(timestamp, provider, "waittime-" + str(wait_time)),
                        provider.value,
                        wait_time,
                    )
                )
        return files

    def run(self, options: RunOptions) -> str or None:
        print("Getting JMeter template...")
        template = ElementTree.ElementTree(file=self.jmeter_template_0)

        if template is None:
            print("No template for test founded!")
            return None

        print("Updating Template for test...")

        self.update_specific_template(options.function_url, options.execution_time, template, self.jmeter_template_0, 1)
        file_name = self.get_output_file_name(options.ts, options.provider, "preexecution")

        run_jmeter(
            file_name,
            self.get_test_name(),
            options.provider.value,
            self.jmeter_template_0,
        )

        print("Pre executions:")
        template = ElementTree.ElementTree(file=self.jmeter_template_1)

        if template is None:
            print("No template for test founded!")
            return None

        print("Updating Template for test...")

        for wait_time in self.wait_time_range:
            info_tet = "\nRun test in {0} after waiting {1} seconds!\n".format(options.provider.value, str(wait_time))
            print(info_tet)

            time.sleep(wait_time)
            self.update_specific_template(get_function_url(options.provider.value, self.get_test_name()), "2", template, self.jmeter_template_1, 1)
            file_name = self.get_output_file_name(options.ts, options.provider, "waittime-" + str(wait_time))

            run_jmeter(
                file_name,
                self.get_test_name(),
                options.provider.value,
                self.jmeter_template_1,
            )
            options.results.append(Result(file_name, options.provider.value, wait_time))

    def plot(self, options: PlotOptions):
        ax = plt.gca()
        color_n = 0

        for result in options.results:
            data = []

            provider = result.provider_name
            wait_time = result.option

            print(
                "\n\nResult for test T {0} in the {1} provider with time since last execution {2}".format(
                    self.get_test_name(), provider, str(wait_time)
                )
            )

            jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + result.file_name
            df = pd.read_csv(jmeter_file)

            print_result_infos(df)
            data.append({"waittime": int(wait_time) / 60, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)
            ax.set_xticks(data_frame["waittime"])
            if provider == "ow":
                provider = "ibm bluemix"

            plot_data_frame(data_frame, "avg", "waittime", colors[color_n], provider, ax)
            color_n += 1

        plt.xlabel("Time Since Last Execution (min)")
        plt.ylabel("Latency (ms)")
        plt.title("Container Reuse Latency")

        save_fig(plt, options.result_path, options.provider, options.ts)
