import os

import matplotlib.pyplot as plt
import pandas as pd
import xml.etree.ElementTree as ElementTree

from Tests.DeployHelper import deploy_test_in_provider
from Tests.IJMeterTest import IJMeterTest
from Tests.PlotHelper import print_result_infos, save_fig
from Tests.Provider import Provider
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    get_jmeter_result_path,
)

from typing import List, Dict


class OverheadTest(IJMeterTest):

    jmeter_template = os.path.join(os.path.dirname(__file__), "Overhead.jmx")

    def get_test_name(self):
        return "T01OverheadTest"

    def run(
        self,
        args: List[str],
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

        run_jmeter(
            file_name, self.get_test_name(), serverless_provider, self.jmeter_template
        )
        # print(str(jmeter_result.decode('UTF-8')))

        file = (file_name, serverless_provider)
        files.append(file)

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
        ax = plt.gca()
        for file in files:
            provider = file[1]
            print(
                "\n\n\n Result for test T {0} in the {1} provider during {2} seconds:".format(
                    self.get_test_name(), provider, execution_time
                )
            )

            jmeter_file = (
                get_jmeter_result_path(self.get_test_name()) + "/" + str(file[0])
            )
            df = pd.read_csv(jmeter_file)
            print_result_infos(df)

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

        save_fig(plt, result_path, serverless_provider, ts)
