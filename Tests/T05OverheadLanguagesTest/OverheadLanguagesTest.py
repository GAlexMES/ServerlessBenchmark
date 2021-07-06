import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd

from ConfigController import read_conf, write_conf
from Tests.DeployHelper import deploy_test_in_provider
from Tests.FunctionInformation import FunctionInformation
from Tests.IJMeterTest import IJMeterTest
from Tests.PlotHelper import print_result_infos, save_fig
from Tests.Provider import Provider
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    get_jmeter_result_path,
)
from typing import List, Dict


class OverheadLanguagesTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "OverheadLanguages.jmx")

    languages = ["Go", "Java", "NodeJs", "Python"]
    supported_providers = [Provider.aws, Provider.ow]

    def get_test_name(self):
        return "T05OverheadLanguagesTest"

    def get_function_paths(self, provider: Provider) -> List[FunctionInformation]:
        config = read_conf()
        functions_info = []
        for prog_lang in self.languages:
            function_dir = "functions/{0}Benchmark{1}".format(provider.value, prog_lang)
            function_path = os.path.join(os.path.dirname(__file__), function_dir)
            function_package_name = config["{0}Functions".format(provider.name)][self.get_test_name()][prog_lang]
            function_url = "{0}".format(function_package_name["function"])
            function_info = FunctionInformation(function_path, function_url, prog_lang)
            functions_info.append(function_info)
        return functions_info

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

        for programming_lang, url in functions.items():
            if url is None or url == "":
                print(
                    "No function in {0} for test {1} on {2} provider".format(
                        programming_lang, self.get_test_name(), serverless_provider
                    )
                )
                return None

            else:
                update_t1_template(url, execution_time, template, self.get_test_name())
                file_name = get_output_file_name(ts, serverless_provider)
                file_name_aux = file_name.split(".")

                file_name_final = create_final_file_name(
                    file_name_aux[0], "Pro_Language", programming_lang, file_name_aux[1]
                )

                run_jmeter(
                    file_name_final,
                    self.get_test_name(),
                    serverless_provider,
                    self.jmeter_template,
                )
                # print(str(jmeter_result.decode('UTF-8')))

                file = (file_name_final, programming_lang)
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
            language = file[1]
            print(
                "\n\n\n Result for test T {0} in the {1} provider during {2} seconds, with {3} as programming language of function:".format(
                    self.get_test_name(),
                    serverless_provider,
                    str(execution_time),
                    language,
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
                label=language,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations of different programming languages during {0} seconds".format(
                execution_time
            )
        )

        save_fig(plt, result_path, serverless_provider, ts)
