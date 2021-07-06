import argparse

from DeployController import *
from TestController import *
from Tests.DeployHelper import deploy_test_in_providers
from Tests.TestRegistry import get_function_for_number
from Tests.Provider import Provider


def main():
    parser = argparse.ArgumentParser(description="Serverless Benchmark Interface!")

    # defining arguments for parser object
    parser.add_argument(
        "-d",
        "--deploy",
        action='store_true',
        help="Deploy in the provider all the functions that are needed for a specified test",
    )

    parser.add_argument(
        "-t",
        "--test",
        action='store_true',
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
        action='store_true',
        help="Remove from the provider all the functions that are needed for a specified test",
    )

    parser.add_argument(
        '-p',
        "--provider",
        type=str,
        default="all",
        help='provider that should be used')

    args = parser.parse_args()

    providers = [Provider.aws, Provider.azure, Provider.ow, Provider.google]
    if args.provider is not None and args.provider != "all":
        providers = [Provider[args.provider]]

    if args.suite is None:
        print("No test suite defined")

    test = get_function_for_number(args.suite)

    if args.deploy is not None and args.deploy:
        deploy_test_in_providers(providers, test)

    if args.test is not None and args.test:
        run_test(test, providers, args.test)

    if args.remove is not None and args.remove:
        remove_functions(args.remove, test)


if __name__ == "__main__":
    # calling the main function
    main()
