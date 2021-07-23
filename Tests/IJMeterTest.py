import os
from typing import List, Dict
import xml.etree.ElementTree as ElementTree

from ConfigController import write_conf, read_conf
from Tests.FunctionInformation import FunctionInformation
from Tests.Provider import Provider

from dataclasses import dataclass

from Tests.TestHelpers import run_jmeter, write_file


@dataclass
class Result:
    file_name: str
    provider_name: str
    option: str or None = None


@dataclass
class PlotOptions:
    results: List[Result]
    execution_time: str
    result_path: str
    provider: str
    ts: int


@dataclass
class RunOptions:
    results: List[Result]
    provider: Provider
    function_url: str or Dict[str, str]
    ts: int
    execution_time: str


class IJMeterTest:
    jmeter_template: str = ""
    supported_providers = [Provider.aws, Provider.ow, Provider.azure, Provider.google]
    required_arguments_count = 0

    def is_test_applicable_for_provider(self, provider: Provider):
        return provider in self.supported_providers

    def check_arguments(self, options: List[str] or None) -> bool:
        return (options is None and self.required_arguments_count == 0) or len(options) == self.required_arguments_count

    def set_arguments(self, options: List[str] or None) -> bool:
        return self.check_arguments(options)

    def save_function_url(self, provider: str, url: str, appendix: str = None):
        config = read_conf()
        if appendix is not None:
            config["functionsURL"][provider][self.get_test_name()][appendix] = url
        else:
            config["functionsURL"][provider][self.get_test_name()] = url
        write_conf(config)

    def get_function_path(self, provider: Provider) -> str:
        return "{0}/functions/{1}Benchmark".format(self.get_test_name(), provider.value)

    def get_function_information(self, provider: Provider) -> List[FunctionInformation]:
        base_function_dir = self.get_function_path(provider)
        function_path = os.path.join(os.path.dirname(__file__), base_function_dir)
        return [FunctionInformation(function_path, None)]

    def update_template(self, url: str, execution_time: str, n_threads: int = 4):
        print(str(n_threads))
        template = ElementTree.ElementTree(file=self.jmeter_template)
        return self.update_specific_template(url, execution_time, template, self.jmeter_template, n_threads)

    def update_specific_template(self, url: str, execution_time: str, template: ElementTree, file_path: str, n_threads: int = 4):
        root = template.getroot()
        for elem in template.iter():
            name = elem.attrib.get("name")
            if name == "ThreadGroup.duration":
                elem.text = execution_time
            elif name == "HTTPSampler.path":
                elem.text = url
            elif name == "ThreadGroup.num_threads":
                elem.text = str(n_threads)

        write_file(root, file_path)

    def run(self, options: RunOptions):
        """Load in the file for extracting text."""
        pass

    def plot(self, options: PlotOptions):
        """Extract text from the currently loaded file."""
        pass

    def get_test_name(self) -> str:
        """Extract text from the currently loaded file."""
        pass

    def generate_result_sets(self, timestamp: int, providers: List[Provider]) -> List[Result]:
        files = []
        for provider in providers:
            files.append(Result(self.get_output_file_name(timestamp, provider), provider.value))
        return files

    def get_output_file_name(self, ts: int, serverless_provider: Provider, addition: str or None = None) -> str:
        if addition is not None:
            return "{0}{1}-{2}_{3}.jtl".format(serverless_provider.value, str(ts), self.get_test_name(), addition)

        return "{0}{1}.jtl".format(serverless_provider.value, str(ts))


class IProviderSpecificJMeterTest(IJMeterTest):

    info_message_format = "No format specified: {0}, {1}, {2}"
    options: Dict[Provider, List[str]] = None

    def generate_result_sets(self, timestamp: int, providers: List[Provider]) -> List[Result]:
        files = []
        for provider in providers:
            for option in self.options[provider]:
                files.append(Result(self.get_output_file_name(timestamp, provider, option), provider.value, option))
        return files

    def get_function_information_for_options(self, provider: Provider, option: str):
        base_function_dir = self.get_function_path(provider)
        function_dir = "{0}{1}".format(base_function_dir, option)
        function_path = os.path.join(os.path.dirname(__file__), function_dir)
        return FunctionInformation(function_path, option)

    def get_function_information(self, provider: Provider) -> List[FunctionInformation]:
        functions_info = []
        for option in self.options.get(provider):
            functions_info.append(self.get_function_information_for_options(provider, option))
        return functions_info

    def run(self, options: RunOptions):

        for option, url in options.function_url.items():
            if url is None or url == "":
                print(self.info_message_format.format(option, self.get_test_name(), options.provider.value))
                continue

            else:
                self.update_template(url, options.execution_time)
                file_name = self.get_output_file_name(options.ts, options.provider, option)

                run_jmeter(
                    file_name,
                    self.get_test_name(),
                    options.provider.value,
                    self.jmeter_template,
                )
                options.results.append(Result(file_name, options.provider.value, option))
