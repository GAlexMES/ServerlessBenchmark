import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd

from Tests.IJMeterTest import IJMeterTest
from Tests.PlotHelper import print_result_infos, save_fig
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    get_jmeter_result_path,
)
from typing import List, Dict


class MemoryTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Memory.jmx")

    def get_test_name(self):
        return "T06MemoryTest"

    def run(
        self,
        args: List[str],
        files: List,
        serverless_provider: str,
        functions: Dict[str, str],
        ts: float,
    ) -> str or None:
        execution_time = args[2]
        template = ElementTree.ElementTree(file=self.jmeter_template)

        for func_mem, url in functions.items():
            if url is None or url == "":
                print(
                    "No function with {0}Mb of memory for test {1} on {2} provider".format(
                        func_mem, self.get_test_name(), serverless_provider
                    )
                )
                return None

            else:
                update_t1_template(url, execution_time, template, self.jmeter_template)
                file_name = get_output_file_name(ts, serverless_provider)
                file_name_aux = file_name.split(".")

                file_name_final = create_final_file_name(
                    file_name_aux[0], "Memory", func_mem, file_name_aux[1]
                )

                run_jmeter(
                    file_name_final,
                    self.get_test_name(),
                    serverless_provider,
                    self.jmeter_template,
                )
                # print(str(jmeter_result.decode('UTF-8')))

                file = (file_name_final, func_mem)
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
            memory = file[1]
            print(
                "\n\n\nResult for test T {0} in the {1} provider during {2} seconds, with {3} of memory of function:".format(
                    self.get_test_name(),
                    serverless_provider,
                    str(execution_time),
                    memory,
                )
            )
            jmeter_file = (
                get_jmeter_result_path(self.get_test_name()) + "/" + str(file[0])
            )
            df = pd.read_csv(jmeter_file)

            print_result_infos(df)

            df.reset_index().plot(
                kind="line",
                y="RealLatency",
                x="index",
                color=colors[color_n],
                label=memory,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations with different memory levels during {0} seconds".format(
                execution_time
            )
        )

        save_fig(plt, result_path, serverless_provider, ts)
