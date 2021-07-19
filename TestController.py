from Tests.IJMeterTest import RunOptions
from Tests.TestHelpers import get_function_url
from ResultController import *

from typing import List


def run_test(jmeter_test: IJMeterTest, providers: List[Provider], ts: int, execution_time: str) -> List[Result] or None:
    test = jmeter_test.get_test_name()
    files = []

    for provider in providers:
        serverless_provider = provider.value

        if not jmeter_test.is_test_applicable_for_provider(provider):
            print("The test is not specified for that provider")
            return None

        print("Updating Template for test...")
        function_url = get_function_url(serverless_provider, test)

        if function_url is None or function_url == "":
            print("No function deployed for test {0} on {1} provider".format(test, serverless_provider))
            continue

        jmeter_test.run(RunOptions(files, provider, function_url, ts, execution_time))

    return files


def get_all_providers(test: str) -> List[str]:
    config = read_conf()
    providers = config["providers"][test]
    return providers
