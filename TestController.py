from Tests.Provider import Provider
from Tests.TestHelpers import get_function_url
from ResultController import *
import time

from typing import List


def run_test(jmeter_test: IJMeterTest, providers: List[Provider], args: List[str]):
    test = jmeter_test.get_test_name()
    ts = int(time.time())
    files = []
    execution_time = ""

    for provider in providers:
        serverless_provider = provider.value

        if not jmeter_test.is_test_applicable_for_provider(provider):
            print("The test is not specified for that provider")
            return None

        print("Updating Template for test...")
        function_url = get_function_url(serverless_provider, test)

        if function_url is None or function_url == "":
            print(
                "No function deployed for test {0} on {1} provider".format(
                    test, serverless_provider
                )
            )
            continue

        test_execution_time = jmeter_test.run(args, files, provider.name, function_url, ts)

        if test_execution_time is not None:
            execution_time = test_execution_time

    print("Calculate the result...")
    result_name = "multiple" if len(providers) != 1 else providers[0]
    plot_result(jmeter_test, files, ts, result_name, execution_time)


def get_all_providers(test: str) -> List[str]:
    config = read_conf()
    providers = config["providers"][test]
    return providers

