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
    get_payload_size,
    append_query_parameter,
    get_jmeter_result_path,
)


class PayloadTest(IJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Payload.jmx")

    def get_test_name(self):
        return "T04PayloadTest"

    def run(self, options: RunOptions) -> str or None:
        execution_time = options.args[2]
        payload_size = get_payload_size(self.get_test_name())
        files_provider = []

        template = ElementTree.ElementTree(file=self.jmeter_template)

        for pay_size in payload_size:
            function_url_with_pay_size = append_query_parameter(options.function_url, str(pay_size))
            update_t1_template(
                function_url_with_pay_size,
                execution_time,
                template,
                self.get_test_name(),
            )
            file_name = get_output_file_name(options.ts, options.provider.value)
            file_name_aux = file_name.split(".")

            file_name_final = create_final_file_name(file_name_aux[0], "payloadSize", str(pay_size), file_name_aux[1])

            run_jmeter(
                file_name_final,
                self.get_test_name(),
                options.provider.valueserverless_provider,
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
                    "Result for test T {0} in the {1} provider with payload size = {2} kb".format(self.get_test_name(), provider, str(payload_size))
                )
                jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + str(file_provider[0])
                df = pd.read_csv(jmeter_file)

                print_result_infos(df)
                data.append({"payloadsize": payload_size, "avg": df["RealLatency"].mean()})

            data_frame = pd.DataFrame(data)
            # ax.set_xticks(data_frame['payloadsize'])
            if provider == "ow":
                provider = "ibm bluemix"
            data_frame.reset_index().plot(
                marker="o",
                kind="line",
                y="avg",
                x="payloadsize",
                color=options.colors[color_n],
                label=provider,
                ax=ax,
            )
            color_n += 1

        execution_time = 900
        plt.xlabel("Payload Size (KBytes)")
        plt.ylabel("Latency (ms)")
        # plt.title('Average latency for payload size during '+str(execution_time)+' seconds')

        save_fig(plt, options.result_path, options.provider.value, options.ts)
