import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd

from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    append_query_parameter,
    get_jmeter_result_path,
)


class WeightTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Weight.jmx")

    def get_test_name(self):
        return "T07WeightTest"

    weights = [0, 5, 10, 15, 20, 25, 30, 35, 40]

    def run(self, options: RunOptions) -> str or None:
        execution_time = self.arguments[0]

        files_provider = []
        template = ElementTree.ElementTree(file=self.jmeter_template)

        for weight in self.weights:
            function_url_appended = append_query_parameter(options.function_url, str(weight))
            update_t1_template(function_url_appended, execution_time, template, self.jmeter_template)
            file_name = get_output_file_name(options.ts, options.provider.value)
            file_name_aux = file_name.split(".")
            file_name_final = create_final_file_name(file_name_aux[0], "fib", str(weight), file_name_aux[1])
            run_jmeter(
                file_name_final,
                self.get_test_name(),
                options.provider.value,
                self.jmeter_template,
            )
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, options.provider.value, weight)
            files_provider.append(file)

        options.files.append(files_provider)
        return execution_time

    def plot(self, options: PlotOptions):
        ax = plt.gca()
        provider = ""
        color_n = 0
        for file in options.files:
            data = []

            for file_provider in file:
                provider = file_provider[1]
                weight = file_provider[2]

                print(
                    "\n\nResult for test T {0} in the {1} provider with N of Fibonacci = {2}:".format(
                        self.get_test_name(), provider, str(weight)
                    )
                )

                jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + str(file_provider[0])
                df = pd.read_csv(jmeter_file)

                print_result_infos(df)
                data.append({"n_of_fib": weight, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)

            if provider == "ow":
                provider = "ibm bluemix"
            data_frame.reset_index().plot(
                marker="o",
                kind="line",
                y="avg",
                x="n_of_fib",
                color=options.colors[color_n],
                label=provider,
                ax=ax,
            )
            color_n += 1

        plt.xlabel("N of sequence of fibonacci ")
        plt.ylabel("Latency (ms)")
        plt.title("Average latency for Fibonacci recursive during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider, options.ts)
