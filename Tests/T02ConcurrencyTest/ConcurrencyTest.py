import os
import matplotlib.pyplot as plt
import pandas as pd

from typing import List

from Colors import colors
from ResultController import Result
from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig, plot_data_frame
from Tests.Provider import Provider
from Tests.TestHelpers import run_jmeter, get_jmeter_result_path


class ConcurrencyTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Concurrency.jmx")
    required_arguments_count = 3

    thread_range = range(0, 1)

    def get_test_name(self):
        return "T02ConcurrencyTest"

    def get_function_path(self, provider: Provider) -> str:
        return "../ServerlessFunctions/SimpleGetEndpoints/{0}GetEndpoint".format(provider.value)

    def generate_result_sets(self, timestamp: int, providers: List[Provider]) -> List[Result]:
        files = []
        for provider in providers:
            for num_threads in self.thread_range:
                files.append(
                    Result(self.get_output_file_name(timestamp, provider, num_threads), provider.value, num_threads)
                )
        return files

    def set_arguments(self, options: List[str] or None) -> bool:
        if super().check_arguments(options):
            self.thread_range = (int(options[0]), int(options[1]) + 1, int(options[2]))
            return True
        return False

    def run(self, options: RunOptions):
        for num_threads in self.thread_range:
            self.update_template(
                options.function_url,
                options.execution_time,
                num_threads,
            )
            file_name = self.get_output_file_name(options.ts, options.provider, num_threads)
            run_jmeter(
                file_name,
                self.get_test_name(),
                options.provider.value,
                self.jmeter_template,
            )

            options.results.append(Result(file_name, options.provider.value, num_threads))

    def plot(self, options: PlotOptions):
        color_n = 0
        fig = plt.figure()
        ax1 = fig.gca()
        ax2 = ax1.twinx()

        for result in options.results:
            data = []
            provider = result.provider_name
            n_threads = result.option
            print(
                "\n\n\n Result for test T {0} in the {1} provider with {2} concurrent requests during {3} seconds:".format(
                    self.get_test_name(), provider, str(n_threads), options.execution_time
                )
            )
            jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + result.file_name
            df = pd.read_csv(jmeter_file)
            print_result_infos(df)

            throughput = (df["RealLatency"].count() - 1) / 900
            print("Throughput " + str(throughput) + "/s")
            data.append(
                {
                    "concurrency": n_threads,
                    "avg": df["RealLatency"].mean(),
                    "throughput": float(throughput),
                }
            )

            data_frame = pd.DataFrame(data)
            # print(pd.DataFrame(data))
            if provider == "ow":
                provider = "ibm bluemix"

            label = "{0} Latency".format(provider)
            plot_data_frame(data_frame, "avg", "concurrency", colors[color_n], label, ax1)
            color_n += 1
            label = "{0} Throughput".format(provider)
            plot_data_frame(data_frame, "throughput", "concurrency", colors[color_n], label, ax2)
            color_n += 1

        ax1.set_ylabel("Average Latency (ms)")
        ax2.set_ylabel("Throughput (1/s)")
        ax1.set_xlabel("Number of concurrent requests")

        plt.title(
            "Average latency and throughput for concurrency level during {0} seconds".format(options.execution_time)
        )
        ax1.legend(frameon=True, loc="best", ncol=1)
        ax2.legend(frameon=True, loc="center left", ncol=1)

        save_fig(plt, options.result_path, options.provider, options.ts)
