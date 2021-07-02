import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd
import time

from typing import List, Dict
from JMeterTemplates.IJMeterTest import IJMeterTest
from JMeterTemplates.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    get_function_url, write_file,
)


class ContainerReuseTest(IJMeterTest):
    jmeter_template_0 = os.path.join(os.path.dirname(__file__), "ContainerReuse_0.jmx")
    jmeter_template_1 = os.path.join(os.path.dirname(__file__), "ContainerReuse_1.jmx")

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
        min_wait_time = int(args[2])
        max_wait_time = int(args[3])
        time_step = int(args[4])
        execution_time = args[5]

        if test_number != "3":
            return None

        files_provider = []

        print("Getting JMeter template...")
        template = ElementTree.ElementTree(file=self.jmeter_template_0)

        if template is None:
            print("No template for test founded!")
            return None

        print("Updating Template for test...")

        update_t1_template(
            function_url, execution_time, template, self.jmeter_template_0
        )
        file_name = get_output_file_name(ts, serverless_provider)
        file_name_aux = file_name.split(".")
        file_name_final = "{0}-{1}.{2}".format(
            file_name_aux[0], "preexecution", file_name_aux[1]
        )

        run_jmeter(file_name_final, test, serverless_provider, self.jmeter_template_0)

        print("Pre executions:")
        template = ElementTree.ElementTree(file=self.jmeter_template_1)

        if template is None:
            print("No template for test founded!")
            return None

        print("Updating Template for test...")

        for wait_time in range(min_wait_time, max_wait_time + 1, time_step):
            info_tet = "\nRun test in {0} after waiting {1} seconds!\n".format(
                serverless_provider, str(wait_time)
            )
            print(info_tet)

            time.sleep(wait_time)

            self.update_t3_template(
                get_function_url(serverless_provider, test),
                template
            )

            file_name = get_output_file_name(ts, serverless_provider)
            file_name_aux = file_name.split(".")
            file_name_final = create_final_file_name(
                file_name_aux[0], "waittime", str(wait_time), file_name_aux[1]
            )

            run_jmeter(
                file_name_final, test, serverless_provider, self.jmeter_template_1
            )
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, serverless_provider, wait_time)
            files_provider.append(file)

        files.append(files_provider)
        return execution_time

    def update_t3_template(self, url: str, template: ElementTree):
        root = template.getroot()

        for elem in template.iter():
            if elem.attrib.get("name") == "HTTPSampler.path":
                elem.text = url

        write_file(root, self.jmeter_template_1)

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
                wait_time = file_provider[2]

                print("\n\n")

                print(
                    "Result for test T"
                    + test_number
                    + " in the "
                    + provider
                    + " provider with time since last execution = "
                    + str(wait_time)
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

                data.append(
                    {"waittime": int(wait_time) / 60, "avg": df["RealLatency"].mean()}
                )

            data_frame = pd.DataFrame(data)
            ax.set_xticks(data_frame["waittime"])
            if provider == "ow":
                provider = "ibm bluemix"
            data_frame.reset_index().plot(
                marker="o",
                kind="line",
                y="avg",
                x="waittime",
                color=colors[color_n],
                label=provider,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("Time Since Last Execution (min)")
        plt.ylabel("Latency (ms)")
        # plt.title('Container Reuse Latency')

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
