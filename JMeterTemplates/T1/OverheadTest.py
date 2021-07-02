import os

import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ElementTree

from JMeterTemplates.IJMeterTest import IJMeterTest
from JMeterTemplates.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    get_jmeter_result_path,
)

from typing import List, Dict


class OverheadTest(IJMeterTest):

    jmeter_template = os.path.join(os.path.dirname(__file__), "Overhead.jmx")

    def run(
        self,
        args: List[str],
        test: str,
        files: List,
        serverless_provider: str,
        function_url: str or Dict[str, str],
        ts: float,
    ) -> str or None:
        test_number = args[1]
        execution_time = args[2]

        if test_number != "1":
            return None
        template = ElementTree.ElementTree(file=self.jmeter_template)

        update_t1_template(function_url, execution_time, template, self.jmeter_template)
        file_name = get_output_file_name(ts, serverless_provider)

        run_jmeter(file_name, test, serverless_provider, self.jmeter_template)
        # print(str(jmeter_result.decode('UTF-8')))

        file = (file_name, serverless_provider)
        files.append(file)

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
        ax = plt.gca()
        for file in files:
            provider = file[1]
            print("\n\n\n")
            print(
                "Result for test T"
                + test_number
                + " in the "
                + provider
                + " provider during "
                + execution_time
                + " seconds:"
            )
            jmeter_file = get_jmeter_result_path(test_number) + "/" + str(file[0])
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
                len(df[df["responseCode"] == 200]) / df["RealLatency"].count() * 100,
            )
            print(
                "% of Failure",
                len(df[df["responseCode"] != 200]) / df["RealLatency"].count() * 100,
            )
            print("Number executions", df["RealLatency"].count())

            if provider == "ow":
                provider = "ibm bluemix"

            df.reset_index().plot(
                kind="line",
                y="RealLatency",
                x="index",
                color=colors[color_n],
                label=provider,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations during " + execution_time + " seconds"
        )

        fig1 = plt.gcf()
        plt.show()

        fig1.savefig(
            str(result_path) + "/" + str(serverless_provider) + "-" + str(ts) + ".png",
            transparent=False,
        )
