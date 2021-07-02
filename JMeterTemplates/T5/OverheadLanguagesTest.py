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
)
from typing import List, Dict


class OverheadLanguagesTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "OverheadLanguages.jmx")

    def run(
        self,
        args: List[str],
        test: str,
        files: List,
        serverless_provider: str,
        functions: Dict[str, str],
        ts: float,
    ) -> str or None:
        execution_time = args[2]

        template = ElementTree.ElementTree(file=self.jmeter_template)

        for programming_lang, url in functions.items():
            if url is None or url == "":
                print(
                    "No function in {0} for test {1} on {2} provider".format(
                        programming_lang, test, serverless_provider
                    )
                )
                return None

            else:
                update_t1_template(url, execution_time, template, test)
                file_name = get_output_file_name(ts, serverless_provider)
                file_name_aux = file_name.split(".")

                file_name_final = create_final_file_name(
                    file_name_aux[0], "Pro_Language", programming_lang, file_name_aux[1]
                )

                run_jmeter(
                    file_name_final, test, serverless_provider, self.jmeter_template
                )
                # print(str(jmeter_result.decode('UTF-8')))

                file = (file_name_final, programming_lang)
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
        ax = plt.gca()
        for file in files:
            df = None

            language = file[1]
            print("\n\n\n")
            print(
                "Result for test T"
                + test_number
                + " in the "
                + serverless_provider
                + " provider during "
                + str(execution_time)
                + " seconds, with "
                + language
                + " as programming language of function:"
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

            df.reset_index().plot(
                kind="line",
                y="RealLatency",
                x="index",
                color=colors[color_n],
                label=language,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations of different programming languages during "
            + execution_time
            + " seconds"
        )

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
