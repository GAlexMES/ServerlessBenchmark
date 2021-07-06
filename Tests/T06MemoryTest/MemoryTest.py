import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt

from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import save_fig, plot_real_latency
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
)


class MemoryTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Memory.jmx")

    def get_test_name(self):
        return "T06MemoryTest"

    # Todo deployment needs to be fied

    def run(self, options: RunOptions) -> str or None:
        execution_time = options.args[2]
        template = ElementTree.ElementTree(file=self.jmeter_template)

        for func_mem, url in options.function_url.items():
            if url is None or url == "":
                print("No function with {0}Mb of memory for test {1} on {2} provider".format(func_mem, self.get_test_name(), options.provider.value))
                return None

            else:
                update_t1_template(url, execution_time, template, self.jmeter_template)
                file_name = get_output_file_name(options.ts, options.provider.value)
                file_name_aux = file_name.split(".")

                file_name_final = create_final_file_name(file_name_aux[0], "Memory", func_mem, file_name_aux[1])

                run_jmeter(
                    file_name_final,
                    self.get_test_name(),
                    options.provider.value,
                    self.jmeter_template,
                )
                # print(str(jmeter_result.decode('UTF-8')))

                file = (file_name_final, func_mem)
                options.files.append(file)

        return execution_time

    def plot(self, options: PlotOptions):
        color_n = 0
        ax = plt.gca()
        for file in options.files:
            memory = file[1]
            print(
                "\n\n\nResult for test T {0} in the {1} provider during {2} seconds, with {3} of memory of function:".format(
                    self.get_test_name(),
                    options.provider.value,
                    options.execution_time,
                    memory,
                )
            )
            plot_real_latency(options.colors[color_n], memory, ax, self.get_test_name(), str(file[0]))
            color_n += 1

        plt.xlabel("Function Invocation Sequence Number")
        plt.ylabel("Latency (ms)")
        plt.title("Latency of a sequence of invocations with different memory levels during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider.value, options.ts)
