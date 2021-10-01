import math
import os
import urllib.request
import time
from typing import List, Dict

from Tests.FunctionInformation import FunctionInformation
from Tests.IJMeterTest import Result, RunOptions, IProviderSpecificJMeterTest
from Tests.Provider import Provider
from Tests.TestHelpers import run_jmeter


class VaryingConcurrencyTest(IProviderSpecificJMeterTest):
    jmeter_template = os.path.join(os.path.dirname(__file__), "VaryingConcurrency.jmx")
    supported_providers = [Provider.aws]
    required_arguments_count = 0
    profile = [
        [1, 5],
        [10, 5],
        [15, 5],
        [20, 5],
        [25, 5],
        [30, 10],
        [28, 7],
        [25, 15],
        [27, 7],
        [29, 2],
        [30, 1],
        [32, 5],
        [29, 2],
        [30, 5],
        [25, 5],
        [20, 5],
        [15, 5],
        [5, 100]
    ]
    options = {
        #Provider.aws: ["Select", "Write", "SelectAgain"],
        Provider.aws: ["Write"],
    }

    def get_test_name(self):
        return "T09VaryingConcurrencyTest"

    def get_function_path(self, provider: Provider) -> str:
        return "{0}/functions/{1}VaryingConcurrency".format(self.get_test_name(), provider.value)

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
            url_dict[type] = options.function_url[type]
            section_cnt = 0
            for section in self.profile:
                section_cnt += 1
                self.update_template(url_dict[type], str(section[1] * 60), section[0])
                file_name_appendix = "{0}-{1}-{2}".format(type, str(section_cnt), math.trunc(time.time() * 1000))
                file_name = self.get_output_file_name(options.ts, options.provider, file_name_appendix)
                run_jmeter(
                    file_name,
                    self.get_test_name(),
                    options.provider.value,
                    self.jmeter_template,
                )

                options.results.append(Result(file_name, options.provider.value, file_name_appendix))



