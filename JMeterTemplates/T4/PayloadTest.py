import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd

from JMeterTemplates.IJMeterTest import IJMeterTest
from JMeterTemplates.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    get_payload_size,
    append_query_parameter,
)

from typing import List, Dict


class PayloadTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Payload.jmx")

    def run(
        self,
        args: List[str],
        test: str,
        files: List,
        serverless_provider: str,
        function_url: str or Dict[str, str],
        ts: float,
    ) -> str or None:
        execution_time = args[2]
        payload_size = get_payload_size(test)
        files_provider = []

        template = ElementTree.ElementTree(file=self.jmeter_template)

        for pay_size in payload_size:
            function_url_with_pay_size = append_query_parameter(
                function_url, str(pay_size)
            )
            update_t1_template(
                function_url_with_pay_size, execution_time, template, test
            )
            file_name = get_output_file_name(ts, serverless_provider)
            file_name_aux = file_name.split(".")

            file_name_final = create_final_file_name(
                file_name_aux[0], "payloadSize", str(pay_size), file_name_aux[1]
            )

            run_jmeter(file_name_final, test, serverless_provider, self.jmeter_template)
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, serverless_provider, pay_size)
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
        ax = plt.gca()
        data = []
        provider = ""

        for file in files:
            data_frame = None
            data = []

            for file_provider in file:
                df = None
                provider = file_provider[1]
                payload_size = file_provider[2]

                print("\n\n")

                print(
                    "Result for test T"
                    + test_number
                    + " in the "
                    + provider
                    + " provider with payload size = "
                    + str(payload_size)
                    + "Kb"
                )
                jmeter_file = (
                    get_jmeter_result_path(test_number) + "/" + str(file_provider[0])
                )
                df = pd.read_csv(jmeter_file)

                df["RealLatency"] = df["elapsed"] - df["Connect"]

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

                data.append(
                    {"payloadsize": payload_size, "avg": df["RealLatency"].mean()}
                )

            data_frame = pd.DataFrame(data)
            # ax.set_xticks(data_frame['payloadsize'])
            if provider == "ow":
                provider = "ibm bluemix"
            data_frame.reset_index().plot(
                marker="o",
                kind="line",
                y="avg",
                x="payloadsize",
                color=colors[color_n],
                label=provider,
                ax=ax,
            )
            color_n += 1

        execution_time = 900
        plt.xlabel("Payload Size (KBytes)")
        plt.ylabel("Latency (ms)")
        # plt.title('Average latency for payload size during '+str(execution_time)+' seconds')

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
