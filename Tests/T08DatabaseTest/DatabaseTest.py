import os
import urllib.request
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from Tests.FunctionInformation import FunctionInformation
from Tests.IJMeterTest import IProviderSpecificJMeterTest, PlotOptions, RunOptions
from Tests.PlotHelper import save_fig, plot_real_latency, plot_data_frame, print_result_infos
from Tests.Provider import Provider
from Tests.TestHelpers import get_jmeter_result_path

instances = 0

class DatabaseTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "Database.jmx")
    supported_providers = [Provider.aws]

    def get_test_name(self):
        return "T08DatabaseTest"

    options = {
        Provider.aws: ["ReadAll", "Write", "ReadAllAgain"],
    }

    def get_function_path(self, provider: Provider) -> str:
        return "{0}/functions/{1}Database".format(self.get_test_name(), provider.value)

    def get_function_information(self, provider: Provider) -> List[FunctionInformation]:
        information = [self.get_function_information_for_options(provider, "Reset")]
        information.extend(super().get_function_information(provider))
        return information

    def run(self, options: RunOptions) -> str or None:
        urllib.request.urlopen(options.function_url["Reset"]).read()
        url_dict: Dict[str, str] = dict()
        for type in self.options[options.provider]:
            url_dict[type] = options.function_url[type] + "?counter=${counter_value}"

        options.function_url = url_dict
        return super().run(options)

    def plot(self, options: PlotOptions):
        ax_whole_process = plt.gca()
        color_n = 0
        results = []
        print(results)
        for result in options.results:
            file_name = result.file_name
            provider = result.provider_name
            type = result.option
            color = options.colors[color_n]
            color_n += 1

            jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + file_name
            df = pd.read_csv(jmeter_file)
            print_result_infos(df)
            df = df.reset_index()
            results.append((provider, type, color, df))

            plot_data_frame(df, "RealLatency", "index", options.colors[color_n], type, ax_whole_process)

            print("\n\nResult for Database {0} test in the {1} provider:".format(type, provider))


        plt.xlabel("something")
        plt.ylabel("Latency (ms)")
        plt.title("Average latency for database access during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider, options.ts)

        def increase_instance(x):
            global instances
            if x == 202:
                instances += 1
            return instances

        for result in results:
            plt.clf()
            instances = 0
            df = result[3]

            df["instances"] = df["responseCode"].apply(increase_instance)
            ax_function = plt.gca()
            plot_data_frame(df, "RealLatency", "index", result[2], result[1], ax_function)
            plot_data_frame(df, "instances", "index", "black", "instances", ax_function)
            plt.xlabel("something")
            plt.ylabel("Latency (ms)")
            plt.title("Average latency for database access during {0} seconds".format(options.execution_time))

            save_fig(plt, options.result_path, "{0}-{1}".format(options.provider,  str(result[1])), options.ts)
