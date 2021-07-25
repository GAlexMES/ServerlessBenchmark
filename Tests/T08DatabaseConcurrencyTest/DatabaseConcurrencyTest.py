import os
import urllib.request
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from Colors import colors, get_complementair
from Tests.FunctionInformation import FunctionInformation
from Tests.IJMeterTest import PlotOptions, RunOptions, IProviderSpecificJMeterTest, Result
from Tests.PlotHelper import save_fig, plot_data_frame, print_result_infos
from Tests.Provider import Provider
from Tests.TestHelpers import get_jmeter_result_path, run_jmeter


class DatabaseConcurrencyTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "DatabaseConcurrency.jmx")
    supported_providers = [Provider.aws]
    required_arguments_count = 3
    thread_range = range(0, 1)
    options = {
        Provider.aws: ["ReadAll", "Write", "ReadAllAgain"],
    }

    def get_test_name(self):
        return "T08DatabaseConcurrencyTest"

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
        urllib.request.urlopen(options.function_url["Reset"]).read()
        url_dict: Dict[str, str] = dict()
        for type in self.options[options.provider]:
            url_dict[type] = options.function_url[type] + "?counter=${counter_value}"
            for num_threads in self.thread_range:
                self.update_template(url_dict[type], options.execution_time, num_threads)
                file_name_appendix = "{0}-{1}".format(type, str(num_threads))
                file_name = self.get_output_file_name(options.ts, options.provider, file_name_appendix)
                run_jmeter(
                    file_name,
                    self.get_test_name(),
                    options.provider.value,
                    self.jmeter_template,
                )

                options.results.append(Result(file_name, options.provider.value, file_name_appendix))

    def plot(self, options: PlotOptions):
        ax_whole_process = plt.gca()
        for provider in options.provider:
            color_n = 0
            results_grouped = []

            def filter_func(x, option_name: str, p: Provider) -> bool:
                return x.option.split("-")[0] == option_name and x.provider_name == p.value

            for option in self.options[provider]:
                results_grouped.append(list(filter(lambda x: filter_func(x, option, provider), options.results)))

            enriched_results_grouped = []
            for results in results_grouped:

                number_of_data_points = 0
                color_n += 1
                color = colors[color_n]
                thread_areas = []
                data_frame = None
                type = ""
                for result in results:
                    file_name = result.file_name
                    type = result.option
                    jmeter_file = get_jmeter_result_path(self.get_test_name()) + "/" + file_name
                    df = pd.read_csv(jmeter_file)
                    print_result_infos(df)

                    df = df.reset_index()
                    df["index"] = df["index"].apply(lambda x: x + number_of_data_points)
                    number_of_data_points = number_of_data_points + df.shape[0]
                    thread_areas.append((type.split("-")[1], number_of_data_points))
                    if data_frame is None:
                        data_frame = df
                    else:
                        data_frame = pd.concat([data_frame, df])

                plot_data_frame(data_frame, "RealLatency", "index", color, type.split("-")[0], ax_whole_process)
                print("\n\nResult for Database {0} test in the {1} provider:".format(type, provider.value))
                enriched_results_grouped.append((color, data_frame, type, thread_areas))

            plt.xlabel("Number of calls")
            plt.ylabel("Latency (ms)")
            ax_whole_process.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, shadow=True)
            plt.title("Average latency for database access during {0} seconds".format(options.execution_time))

            save_fig(plt, options.result_path, provider.value, options.ts)

            for result in enriched_results_grouped:
                plt.clf()
                ax_function = plt.gca()
                ax2 = ax_function.twinx()
                df = result[1]
                type = result[2].split("-")[0]

                def map(x):
                    if x == 202:
                        return 1
                    return 0

                response_codes = df["responseCode"].to_numpy()
                new_instances = [map(x) for x in response_codes]
                new_instances_acc = np.cumsum(new_instances, dtype=int)
                df["instances"] = new_instances_acc

                start = 0
                alpha = 0.0
                for thread_area in result[3]:
                    label = "{0} threads".format(thread_area[0])
                    plt.axvspan(start, thread_area[1], facecolor='grey',  alpha=alpha, label=label)
                    start = thread_area[1]
                    alpha = alpha + 0.05

                ax_function.hlines(df["RealLatency"].mean(), -10, df.shape[0]+10, label="Average latency", zorder=10)
                plot_data_frame(df, "RealLatency", "index", result[0], type, ax_function)
                plot_data_frame(df, "instances", "index", get_complementair(result[0]), "instances", ax2)

                h1, l1 = ax_function.get_legend_handles_labels()
                h2, l2 = ax2.get_legend_handles_labels()
                ax_function.get_legend().remove()
                ax2.get_legend().remove()
                plt.legend(h1+h2, l1+l2, bbox_to_anchor=(1.05, 1.0), loc='upper left')
                plt.tight_layout()
                ax2.set_ylabel('instances')
                ax_function.set_ylabel('Latency (ms)')
                ax2.set_xlabel("Request index")
                ax_function.set_xlabel("Request index")
                plt.xlabel("Request index")
                plt.title("Latency for database access")
                save_fig(plt, options.result_path, "{0}-{1}".format(provider.value, type), options.ts)
