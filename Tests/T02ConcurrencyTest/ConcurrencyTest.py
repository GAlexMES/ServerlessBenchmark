import os

import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ElementTree

from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig, plot_data_frame
from Tests.TestHelpers import (
    get_output_file_name,
    run_jmeter,
    get_jmeter_result_path,
    create_final_file_name,
    update_t2_template,
    get_running_data,
)


class ConcurrencyTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Concurrency.jmx")
    required_arguments_count = 4

    def get_test_name(self):
        return "T02ConcurrencyTest"

    def run(self, options: RunOptions) -> str or None:
        min_concurrency = int(self.arguments[0])
        max_concurrency = int(self.arguments[1])
        concurrency_step = int(self.arguments[2])
        execution_time = self.arguments[3]

        files_provider = []

        template = ElementTree.ElementTree(file=self.jmeter_template)
        for num_threads in range(min_concurrency, max_concurrency + 1, concurrency_step):
            update_t2_template(
                options.function_url,
                execution_time,
                template,
                self.jmeter_template,
                num_threads,
            )
            file_name = get_output_file_name(options.ts, options.provider.value)
            file_name_aux = file_name.split(".")
            file_name_final = create_final_file_name(
                file_name_aux[0], "concurrency", str(num_threads), file_name_aux[1]
            )
            jmeter_result = run_jmeter(
                file_name_final,
                self.get_test_name(),
                options.provider.value,
                self.jmeter_template,
            )
            # print(str(jmeter_result.decode('UTF-8')))

            throughput = get_running_data(str(jmeter_result.decode("UTF-8")))

            file = (file_name_final, options.provider.value, num_threads, throughput)
            files_provider.append(file)
        options.files.append(files_provider)
        return execution_time

    def plot(self, options: PlotOptions):
        color_n = 0
        fig = plt.figure()
        ax1 = fig.gca()
        ax2 = ax1.twinx()

        provider = ""
        for file in options.files:
            data = []
            for file_provider in file:

                provider = file_provider[1]
                n_threads = file_provider[2]
                print(
                    "\n\n\n Result for test T {0} in the {1} provider with {2} concurrent requests during {3} seconds:".format(
                        self.get_test_name(), provider, str(n_threads), options.execution_time
                    )
                )
                jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + str(file_provider[0])
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
            plot_data_frame(data_frame, "avg", "concurrency", options.colors[color_n], label, ax1)
            color_n += 1
            label = "{0} Throughput".format(provider)
            plot_data_frame(data_frame, "throughput", "concurrency", options.colors[color_n], label, ax2)
            color_n += 1

        ax1.set_ylabel("Average Latency (ms)")
        ax2.set_ylabel("Throughput (1/s)")
        ax1.set_xlabel("Number of concurrent requests")

        # plt.title('Average latency and throughput for concurrency level during '+str(execution_time)+' seconds')
        ax1.legend(frameon=True, loc="best", ncol=1)
        ax2.legend(frameon=True, loc="center left", ncol=1)
        # plt.legend()

        save_fig(plt, options.result_path, options.provider, options.ts)
