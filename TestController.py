from JMeterTemplates.T1.OverheadTest import OverheadTest
from JMeterTemplates.T2.ConcurrencyTest import ConcurrencyTest
from JMeterTemplates.T3.ContainerReuseTest import ContainerReuseTest
from JMeterTemplates.T4.PayloadTest import PayloadTest
from JMeterTemplates.T5.OverheadLanguagesTest import OverheadLanguagesTest
from JMeterTemplates.T6.MemoryTest import MemoryTest
from JMeterTemplates.T7.WeightTest import WeightTest
from JMeterTemplates.TestHelpers import get_function_url
from ResultController import *
import time

from typing import List


def run_test(args):
    test_number = args[1]

    if test_number == "1":
        run_jmeter_test(OverheadTest(), args)
    elif test_number == "2":
        run_jmeter_test(ConcurrencyTest(), args)
    elif test_number == "3":
        run_jmeter_test(ContainerReuseTest(), args)
    elif test_number == "4":
        run_jmeter_test(PayloadTest(), args)
    elif test_number == "5":
        run_jmeter_test(OverheadLanguagesTest(), args)
    elif test_number == "6":
        run_jmeter_test(MemoryTest(), args)
    elif test_number == "7":
        run_jmeter_test(WeightTest(), args)


def run_jmeter_test(jmeter_test: IJMeterTest, args: List[str]):
    serverless_provider = args[0].lower()
    test_number = args[1]

    test = "T{0}".format(test_number)
    ts = int(time.time())
    files = []
    execution_time = ""

    serverless_providers = (
        get_all_providers(test)
        if serverless_provider == "all"
        else [serverless_provider]
    )

    for provider in serverless_providers:

        if not verify_test_provider(test, serverless_provider):
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

        test_execution_time = jmeter_test.run(
            args, test, files, provider, function_url, ts
        )

        if test_execution_time is not None:
            execution_time = test_execution_time

    print("Calculate the result...")
    result_name = "all" if serverless_provider == "all" else serverless_provider
    plot_result(jmeter_test, test_number, files, ts, result_name, execution_time)


def get_all_providers(test: str) -> List[str]:
    config = read_conf()
    providers = config["providers"][test]
    return providers


def verify_test_provider(test: str, provider: str) -> bool:
    config = read_conf()
    providers = config["providers"][test]

    if provider in providers:
        return True
    return False
