import os

import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ElementTree

from JMeterTemplates.IJMeterTest import IJMeterTest
from JMeterTemplates.TestHelpers import (
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

    def run(
        self,
        args: List[str],
        test: str,
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
                file_name_final, test, serverless_provider, self.jmeter_template
            )
            # print(str(jmeter_result.decode('UTF-8')))

            throughput = get_running_data(str(jmeter_result.decode("UTF-8")))

            file = (file_name_final, serverless_provider, num_threads, throughput)
            files_provider.append(file)
        files.append(files_provider)
        return execution_time

    def plot(
        self,
        test_number: str,
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

        data = []
        provider = ""
        data_frame = None
        for file in files:
            data_frame = None
            data = []
            df = None
            for file_provider in file:

                provider = file_provider[1]
                n_threads = file_provider[2]
                throughput = file_provider[3]
                print("\n\n\n")
                print(
                    "Result for test T"
                    + test_number
                    + " in the "
                    + provider
                    + " provider with "
                    + str(n_threads)
                    + " concurrent requests during "
                    + str(execution_time)
                    + " seconds"
                )
                jmeter_file = (
                    get_jmeter_result_path(test_number) + "/" + str(file_provider[0])
                )
                df = pd.read_csv(jmeter_file)
                df["RealLatency"] = df["Latency"] - df["Connect"]
                print("Max Latency:", df["RealLatency"].max())
                print("Min Latency: ", df["RealLatency"].min())
                print("Avg Latency:", df["RealLatency"].mean())
                print("Std Latency", df["RealLatency"].std())
                print("10th percentile: ", df["RealLatency"].quantile(0.1))
                print("90th percentile: ", df["RealLatency"].quantile(0.9))
                print(
                    "% of Success",
                    len(df[df["responseCode"] == 200])
                    / df["RealLatency"].count()
                    * 100,
                )
                print(
                    "% of Failure",
                    len(df[df["responseCode"] != 200])
                    / df["RealLatency"].count()
                    * 100,
                )
                print("Number executions", df["RealLatency"].count())
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

        fig1 = plt.gcf()
        plt.show()

        fig1.savefig(
            str(result_path) + "/" + str(serverless_provider) + "-" + str(ts) + ".png",
            transparent=False,
        )
        fig1.savefig(
            str(result_path) + "/" + str(serverless_provider) + "-" + str(ts) + ".pdf",
            transparent=False,
        )
