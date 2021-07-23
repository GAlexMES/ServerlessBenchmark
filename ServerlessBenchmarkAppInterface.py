import argparse
import time

from TestController import *
from Tests.DeployHelper import deploy_test_in_providers, remove_from_providers
from Tests.TestRegistry import get_function_for_number
from Tests.Provider import Provider


def main():
    parser = argparse.ArgumentParser(description="Serverless Benchmark Interface!")

    # defining arguments for parser object
    parser.add_argument(
        "-d",
        "--deploy",
        action="store_true",
        help="Deploy in the provider all the functions that are needed for a specified test",
    )

    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help="Run in the provider all the functions that are needed for the specified test",
    )

    parser.add_argument(
        "-s",
        "--suite",
        type=int,
        required=True,
        help="Run in the provider all the functions that are needed for the specified test",
    )

    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Remove from the provider all the functions that are needed for a specified test",
    )

    parser.add_argument(
        "-e",
        "--export",
        type=int,
        default=None,
        const=-1,
        nargs="?",
        help="Run in the provider all the functions that are needed for the specified test",
    )

    parser.add_argument(
        "-x",
        "--execution_time",
        type=str,
        default="90",
        nargs="?",
        help="Run in the provider all the functions that are needed for the specified test",
    )

    parser.add_argument(
        "-o",
        "--options",
        type=str,
        nargs="*",
        help="Run in the provider all the functions that are needed for the specified test",
    )

    parser.add_argument("-p", "--provider", type=str, default="all", help="provider that should be used")

    args = parser.parse_args()

    providers = [Provider.aws, Provider.azure, Provider.ow, Provider.google]
    if args.provider is not None and args.provider != "all":
        providers = [Provider[args.provider]]

    if args.suite is None:
        print("No test suite defined")

    test = get_function_for_number(args.suite)

    if test is None:
        return

    if args.deploy is not None and args.deploy:
        deploy_test_in_providers(providers, test)

    timestamp = int(time.time()) if args.export is None or args.export == -1 else args.export

    execution_time = args.execution_time
    results: List[Result] = []

    if (args.test is not None and args.test) or args.export is not None:
        if not test.set_arguments(args.options):
            print(
                "The options {0} do not have the right amount of arguments for {1}".format(
                    args.options, test.get_test_name()
                )
            )
            return

    if args.test is not None and args.test:
        results = run_test(test, providers, timestamp, execution_time)

    if args.export is not None:
        if results is not None and len(results) == 0:
            results = test.generate_result_sets(timestamp, providers)
            print(results)

        plot_result(test, results, timestamp, providers, execution_time)

    if args.remove is not None and args.remove:
        remove_from_providers(providers, test)


if __name__ == "__main__":
    # calling the main function
    main()
