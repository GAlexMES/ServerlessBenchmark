import os
from typing import List, Dict

from ConfigController import write_conf, read_conf
from Tests.FunctionInformation import FunctionInformation
from Tests.Provider import Provider


class IJMeterTest:
    supported_providers = [Provider.aws, Provider.ow, Provider.azure, Provider.google]

    def is_test_applicable_for_provider(self, provider: Provider):
        return provider in self.supported_providers

    def save_function_url(self, provider: str, url: str, appendix: str = None):
        config = read_conf()
        if appendix is not None:
            config["functionsURL"][provider][self.get_test_name()][appendix] = url
        else:
            config["functionsURL"][provider][self.get_test_name()] = url
        write_conf(config)

    def get_function_paths(self, provider: Provider) -> List[FunctionInformation]:
        config = read_conf()
        function_dir = "{0}/functions/{1}Benchmark".format(self.get_test_name(), provider.value)
        function_path = os.path.join(os.path.dirname(__file__), function_dir)
        function_package_name = config["{0}Functions".format(provider.name)][self.get_test_name()]
        function_url = "{1}".format(function_package_name["function"])
        function_info = FunctionInformation(function_path, function_url)
        return [function_info]

    def run(
        self,
        args: List[str],
        files: List,
        serverless_provider: str,
        function_url: str or Dict[str, str],
        ts: float,
    ) -> str or None:
        """Load in the file for extracting text."""
        pass

    def plot(
        self,
        files: List,
        execution_time: str,
        colors: List[str],
        result_path: str,
        serverless_provider: str,
        ts: float,
    ):
        """Extract text from the currently loaded file."""
        pass

    def get_test_name(self) -> str:
        """Extract text from the currently loaded file."""
        pass
