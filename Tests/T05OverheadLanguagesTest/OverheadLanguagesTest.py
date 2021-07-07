import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt

from Tests.IJMeterTest import  PlotOptions, RunOptions, IJMeterOptionalTest
from Tests.PlotHelper import save_fig, plot_real_latency
from Tests.Provider import Provider
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
)


class OverheadLanguagesTest(IJMeterOptionalTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "OverheadLanguages.jmx")

    options = {
        Provider.aws: ["Go", "Java", "NodeJs", "Python"],
        Provider.ow: ["NodeJs", "Php", "Python", "Ruby", "Swift"],
    }
    supported_providers = [Provider.aws, Provider.ow]

    def get_test_name(self):
        return "T05OverheadLanguagesTest"

    def run(self, options: RunOptions) -> str or None:
        execution_time = options.args[2]

        template = ElementTree.ElementTree(file=self.jmeter_template)

        for programming_lang, url in options.function_url.items():
            if url is None or url == "":
                print(
                    "No function in {0} for test {1} on {2} provider".format(
                        programming_lang, self.get_test_name(), options.provider.value
                    )
                )
                return None

            else:
                update_t1_template(url, execution_time, template, self.get_test_name())
                file_name = get_output_file_name(options.ts, options.provider.value)
                file_name_aux = file_name.split(".")

                file_name_final = create_final_file_name(
                    file_name_aux[0], "Pro_Language", programming_lang, file_name_aux[1]
                )

                run_jmeter(
                    file_name_final,
                    self.get_test_name(),
                    options.provider.value,
                    self.jmeter_template,
                )
                # print(str(jmeter_result.decode('UTF-8')))

                file = (file_name_final, programming_lang)
                options.files.append(file)
        return execution_time

    def plot(self, options: PlotOptions):
        color_n = 0
        ax = plt.gca()
        for file in options.files:
            language = file[1]
            print(
                "\n\n\n Result for test T {0} in the {1} provider during {2} seconds, with {3} as programming language of function:".format(
                    self.get_test_name(),
                    options.provider.value,
                    options.execution_time,
                    language,
                )
            )
            plot_real_latency(options.colors[color_n], language, ax, self.get_test_name(), str(file[0]))
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title(
            "Latency of a sequence of invocations of different programming languages during {0} seconds".format(
                options.execution_time
            )
        )

        save_fig(plt, options.result_path, options.provider.value, options.ts)
