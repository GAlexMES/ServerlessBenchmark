import os

import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ElementTree

from Tests.DeployHelper import deploy_test_in_provider
from Tests.IJMeterTest import IJMeterTest
from Tests.PlotHelper import print_result_infos, save_fig
from Tests.Provider import Provider
from Tests.TestHelpers import (
    get_output_file_name,
    run_jmeter,
    get_jmeter_result_path,
    create_final_file_name,
    update_t2_template,
    get_running_data,
)

from typing import List, Dict


class ConcurrencyTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Concurrency.jmx")

    def get_test_name(self):
        return "T02ConcurrencyTest"

    def run(
        self,
        args: List[str],
        files: List,
        serverless_provider: str,
        function_url: str or Dict[str, str],
        ts: float,
    ) -> str or None:
        min_concurrency = int(args[2])
        max_concurrency = int(args[3])
        concurrency_step = int(args[4])
        execution_time = args[5]

        files_provider = []

        template = ElementTree.ElementTree(file=self.jmeter_template)
        for num_threads in range(
            min_concurrency, max_concurrency + 1, concurrency_step
        ):
            update_t2_template(
                function_url,
                execution_time,
                template,
                self.jmeter_template,
                num_threads,
            )
            file_name = get_output_file_name(ts, serverless_provider)
            file_name_aux = file_name.split(".")
            file_name_final = create_final_file_name(
                file_name_aux[0], "concurrency", str(num_threads), file_name_aux[1]
            )
            jmeter_result = run_jmeter(
                file_name_final,
                self.get_test_name(),
                serverless_provider,
                self.jmeter_template,
            )
            # print(str(jmeter_result.decode('UTF-8')))

            throughput = get_running_data(str(jmeter_result.decode("UTF-8")))

            file = (file_name_final, serverless_provider, num_threads, throughput)
            files_provider.append(file)
        files.append(files_provider)
        return execution_time

    def plot(
        self,
        files: List,
        execution_time: str,
        colors: List[str],
        result_path: str,
        serverless_provider: str,
        ts: float,
    ):
        color_n = 0
        fig = plt.figure()
        ax1 = fig.gca()
        ax2 = ax1.twinx()

        provider = ""
        for file in files:
            data = []
            for file_provider in file:

                provider = file_provider[1]
                n_threads = file_provider[2]
                print(
                    "\n\n\n Result for test T {0} in the {1} provider with {2} concurrent requests during {3} seconds:".format(
                        self.get_test_name(), provider, str(n_threads), execution_time
                    )
                )
                jmeter_file = (
                    get_jmeter_result_path(self.get_test_name())
                    + "/"
                    + str(file_provider[0])
                )
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
            data_frame.plot(
                marker="o",
                kind="line",
                y="avg",
                x="concurrency",
                color=colors[color_n],
                label=provider + " Latency",
                ax=ax1,
            )
            color_n += 1
            data_frame.plot(
                marker="o",
                kind="line",
                y="throughput",
                x="concurrency",
                color=colors[color_n],
                label=provider + " Throughput",
                ax=ax2,
            )
            color_n += 1

        ax1.set_ylabel("Average Latency (ms)")
        ax2.set_ylabel("Throughput (1/s)")
        ax1.set_xlabel("Number of concurrent requests")

        # plt.title('Average latency and throughput for concurrency level during '+str(execution_time)+' seconds')
        ax1.legend(frameon=True, loc="best", ncol=1)
        ax2.legend(frameon=True, loc="center left", ncol=1)
        # plt.legend()

        save_fig(plt, result_path, serverless_provider, ts)