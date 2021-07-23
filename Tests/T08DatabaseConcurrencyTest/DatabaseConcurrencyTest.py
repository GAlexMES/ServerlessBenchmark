import os
import urllib.request
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from Colors import colors, get_complementair
from Tests.FunctionInformation import FunctionInformation
from Tests.IJMeterTest import PlotOptions, RunOptions, IProviderSpecificJMeterTest, Result
from Tests.PlotHelper import save_fig, plot_data_frame, print_result_infos
from Tests.Provider import Provider
from Tests.TestHelpers import get_jmeter_result_path, run_jmeter

instances = 0


class DatabaseConcurrencyTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "DatabaseConcurrency.jmx")
    supported_providers = [Provider.aws]
    required_arguments_count = 3
    thread_range = range(0, 1)
    options = {
        Provider.aws: ["ReadAll", "Write", "ReadAllAgain"],
    }

    def get_test_name(self):
        return "T09DatabaseConcurrencyTest"

    def set_arguments(self, options: List[str] or None) -> bool:
        if super().check_arguments(options):
            self.thread_range = range(int(options[0]), int(options[1]) + 1, int(options[2]))
            return True
        return False

    def get_function_path(self, provider: Provider) -> str:
        return "{0}/functions/{1}Database".format(self.get_test_name(), provider.value)

    def get_function_information(self, provider: Provider) -> List[FunctionInformation]:
        information = [self.get_function_information_for_options(provider, "Reset")]
        information.extend(super().get_function_information(provider))
        return information

    def generate_result_sets(self, timestamp: int, providers: List[Provider]) -> List[Result]:
        files = []
        for provider in providers:
            for type in self.options[provider]:
                for num_threads in self.thread_range:
                    option = "{0}-{1}".format(type, str(num_threads))
                    file_name = self.get_output_file_name(timestamp, provider, option)
                    files.append(Result(file_name, provider.value, option))
        return files

    def run(self, options: RunOptions):
        #urllib.request.urlopen(options.function_url["Reset"]).read()
        url_dict: Dict[str, str] = dict()
        for type in self.options[options.provider]:
            url_dict[type] = options.function_url[type] + "?counter=${counter_value}"
            for num_threads in self.thread_range:
                self.update_template(url_dict[type], options.execution_time, num_threads)
                file_name = self.get_output_file_name(options.ts, options.provider, "{0}-{1}".format(type, str(num_threads)))
                run_jmeter(
                    file_name,
                    self.get_test_name(),
                    options.provider.value,
                    self.jmeter_template,
                )

                options.results.append(Result(file_name, options.provider.value,  "{0}-{1}".format(type, str(num_threads))))

    def plot(self, options: PlotOptions):
        ax_whole_process = plt.gca()
        color_n = 0
        results = []
        for result in options.results:
            file_name = result.file_name
            provider = result.provider_name
            type = result.option
            color = colors[color_n]
            color_n += 1

            jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + file_name
            df = pd.read_csv(jmeter_file)
            print_result_infos(df)
            df = df.reset_index()
            results.append((provider, file_name, color, df, type))

            plot_data_frame(df, "RealLatency", "index", colors[color_n], type, ax_whole_process)

            print("\n\nResult for Database {0} test in the {1} provider:".format(type, provider))

        plt.xlabel("something")
        plt.ylabel("Latency (ms)")
        plt.title("Average latency for database access during {0} seconds".format(options.execution_time))

        save_fig(plt, options.result_path, options.provider, options.ts)

        results_grouped = []
        results_grouped.append(filter(lambda x: x[4].split("-")[0] == "ReadAll", results))
        results_grouped.append(filter(lambda x: x[4].split("-")[0] == "Write", results))
        results_grouped.append(filter(lambda x: x[4].split("-")[0] == "ReadAllAgain", results))

        def increase_instance(x):
            global instances
            if x == 202:
                instances += 1
            return instances

        # TODO DATA ALL BAD GATEWAY

        for result_group in results_grouped:
            plt.clf()
            instances = 0
            number_of_data_points = 0
            type = ""
            ax_function = plt.gca()
            ax2 = ax_function.twinx()
            for result in result_group:
                df = result[3]
                type = result[4].split("-")[0]
                threads = result[4].split("-")[1]
                df["instances"] = df["responseCode"].apply(increase_instance)
                df["index"] = df["index"].apply(lambda x: x + number_of_data_points)
                number_of_data_points = number_of_data_points + df.shape[0]
                plot_data_frame(df, "RealLatency", "index", result[2], result[4], ax_function)
                plot_data_frame(df, "instances", "index", get_complementair(result[2]), "instances-"+threads, ax2)

            plt.xlabel("request")
            plt.ylabel("Latency (ms)")
            plt.title("Average latency for database access during {0} seconds".format(options.execution_time))

            save_fig(plt, options.result_path, "{0}-{1}".format(options.provider, type), options.ts)
