import os
import xml.etree.ElementTree as ElementTree
import matplotlib.pyplot as plt
import pandas as pd

from Tests.IJMeterTest import IJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import print_result_infos, save_fig, plot_data_frame
from Tests.TestHelpers import (
    update_t1_template,
    get_output_file_name,
    run_jmeter,
    create_final_file_name,
    append_query_parameter,
    get_jmeter_result_path,
)


class PayloadTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Payload.jmx")

    payload_sizes = [0, 32, 64, 96, 128, 160, 192, 224, 256]

    def get_test_name(self):
        return "T04PayloadTest"

    def run(self, options: RunOptions) -> str or None:
        execution_time = self.arguments[0]
        files_provider = []
        template = ElementTree.ElementTree(file=self.jmeter_template)

        for pay_size in self.payload_sizes:
            function_url_with_pay_size = append_query_parameter(options.function_url, str(pay_size))
            update_t1_template(
                function_url_with_pay_size,
                execution_time,
                template,
                self.jmeter_template,
            )
            file_name = get_output_file_name(options.ts, options.provider.value)
            file_name_aux = file_name.split(".")

            file_name_final = create_final_file_name(file_name_aux[0], "payloadSize", str(pay_size), file_name_aux[1])

            run_jmeter(
                file_name_final,
                self.get_test_name(),
                options.provider.value,
                self.jmeter_template,
            )
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, options.provider.value, pay_size)
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
                payload_size = file_provider[2]

                print("\n\n")

                print(
                    "Result for test T {0} in the {1} provider with payload size = {2} kb".format(
                        self.get_test_name(), provider, str(payload_size)
                    )
                )
                jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + str(file_provider[0])
                df = pd.read_csv(jmeter_file)

                print_result_infos(df)
                data.append({"payloadsize": payload_size, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)
            # ax.set_xticks(data_frame['payloadsize'])
            if provider == "ow":
                provider = "ibm bluemix"
            plot_data_frame(data_frame, "avg", "payloadsize", options.colors[color_n], provider, ax)
            color_n += 1

        plt.xlabel("Payload Size (KBytes)")
        plt.ylabel("Latency (ms)")
        # plt.title('Average latency for payload size during '+str(execution_time)+' seconds')

        save_fig(plt, options.result_path, options.provider, options.ts)
