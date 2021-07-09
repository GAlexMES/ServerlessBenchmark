import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd
import time

from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig, plot_data_frame
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    get_function_url,
    write_file,
    get_jmeter_result_path,
)


class ContainerReuseTest(IJMeterTest):
    jmeter_template_0 = os.path.join(os.path.dirname(__file__), "ContainerReuse_0.jmx")
    jmeter_template_1 = os.path.join(os.path.dirname(__file__), "ContainerReuse_1.jmx")

    required_arguments_count = 4

    def get_test_name(self):
        return "T03ContainerReuseTest"

    def run(self, options: RunOptions) -> str or None:
        min_wait_time = int(self.arguments[0])
        max_wait_time = int(self.arguments[1])
        time_step = int(self.arguments[2])
        execution_time = self.arguments[3]

        files_provider = []

        print("Getting JMeter template...")
        template = ElementTree.ElementTree(file=self.jmeter_template_0)

        if template is None:
            print("No template for test founded!")
            return None

        print("Updating Template for test...")

        update_t1_template(options.function_url, execution_time, template, self.jmeter_template_0)
        file_name = get_output_file_name(options.ts, options.provider.value)
        file_name_aux = file_name.split(".")
        file_name_final = "{0}-{1}.{2}".format(file_name_aux[0], "preexecution", file_name_aux[1])

        run_jmeter(
            file_name_final,
            self.get_test_name(),
            options.provider.value,
            self.jmeter_template_0,
        )

        print("Pre executions:")
        template = ElementTree.ElementTree(file=self.jmeter_template_1)

        if template is None:
            print("No template for test founded!")
            return None

        print("Updating Template for test...")

        for wait_time in range(min_wait_time, max_wait_time + 1, time_step):
            info_tet = "\nRun test in {0} after waiting {1} seconds!\n".format(options.provider.value, str(wait_time))
            print(info_tet)

            time.sleep(wait_time)

            self.update_t3_template(get_function_url(options.provider.value, self.get_test_name()), template)

            file_name = get_output_file_name(options.ts, options.provider.value)
            file_name_aux = file_name.split(".")
            file_name_final = create_final_file_name(file_name_aux[0], "waittime", str(wait_time), file_name_aux[1])

            run_jmeter(
                file_name_final,
                self.get_test_name(),
                options.provider.value,
                self.jmeter_template_1,
            )
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, options.provider.value, wait_time)
            files_provider.append(file)

        options.files.append(files_provider)
        return execution_time

    def update_t3_template(self, url: str, template: ElementTree):
        root = template.getroot()

        for elem in template.iter():
            if elem.attrib.get("name") == "HTTPSampler.path":
                elem.text = url

        write_file(root, self.jmeter_template_1)

    def plot(self, options: PlotOptions):
        ax = plt.gca()
        provider = ""
        color_n = 0

        for file in options.files:
            data = []

            for file_provider in file:
                provider = file_provider[1]
                wait_time = file_provider[2]

                print(
                    "\n\nResult for test T {0} in the {1} provider with time since last execution {2}".format(
                        self.get_test_name(), provider, str(wait_time)
                    )
                )

                jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + str(file_provider[0])
                df = pd.read_csv(jmeter_file)

                print_result_infos(df)
                data.append({"waittime": int(wait_time) / 60, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)
            ax.set_xticks(data_frame["waittime"])
            if provider == "ow":
                provider = "ibm bluemix"

            plot_data_frame(data_frame, "avg", "waittime", options.colors[color_n], provider, ax)
            color_n += 1

        plt.xlabel("Time Since Last Execution (min)")
        plt.ylabel("Latency (ms)")
        # plt.title('Container Reuse Latency')

        save_fig(plt, options.result_path, options.provider, options.ts)
