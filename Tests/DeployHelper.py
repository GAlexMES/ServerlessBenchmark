import os
import subprocess

from ConfigController import *
from Tests.IJMeterTest import IJMeterTest
from Tests.Provider import Provider
from typing import List


def deploy_test_in_providers(providers: List[Provider], test: IJMeterTest):
    for provider in providers:
        deploy_test_in_provider(provider, test)


def deploy_test_in_provider(provider: Provider, test: IJMeterTest):
    functions_info = test.get_function_information(provider)
    for function_info in functions_info:
        serverless_deploy_response = deploy(function_info.path, provider)
        function_url = get_function_url(
            provider,
            serverless_deploy_response,
            function_info.url,
            test.get_test_name(),
        )

        if function_url is not None:
            test.save_function_url(provider.value, function_url, function_info.detail)
            print(
                "Function(s) for specified test is deployed with success on AWS!\nThe url of function is: {0}".format(
                    function_url
                )
            )
        else:
            print("Error deploying:\n {0}".format(str(serverless_deploy_response.decode("UTF-8"))))


def remove_from_providers(providers: List[Provider], test: IJMeterTest):
    for provider in providers:
        remove_from_provider(provider, test)


def remove_from_provider(provider: Provider, test: IJMeterTest):
    print("Removing function(s) for test {0} of provider {1}".format(test.get_test_name(), provider.value))
    functions_info = test.get_function_information(provider)
    for function_info in functions_info:
        remove(function_info.path)
        test.save_function_url(provider.value, "", function_info.detail)


def deploy(function_path: str, provider: Provider):
    print("Deploy function in {0}".format(function_path))
    install(function_path)
    build(function_path)
    try:
        if provider == Provider.google:
            return subprocess.check_output(
                ["serverless", "deploy", "-v", "--region", "europe-west1"],
                cwd=function_path,
            )
        else:
            return subprocess.check_output(
                ["serverless", "deploy", "-v"],
                stderr=subprocess.STDOUT,
                cwd=function_path,
            )

    except subprocess.CalledProcessError as e:
        raise RuntimeError("command {0} return with error (code {1}): {2}".format(e.cmd, e.returncode, e.output))


def remove(function_path):
    try:
        return subprocess.check_output(["serverless", "remove"], cwd=function_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command {0} return with error (code {1}): {2}".format(e.cmd, e.returncode, e.output))


def install(function_path: str):
    if os.path.isfile("{0}/go.mod".format(function_path)):
        subprocess.check_output(
            ["go", "mod", "download"],
            cwd=function_path,
        )


def build(function_path: str):
    if os.path.isfile("{0}/Makefile".format(function_path)):
        subprocess.check_output(
            ["make", "build"],
            cwd=function_path,
        )

    if os.path.isfile("{0}/build.gradle.kts".format(function_path)):
        subprocess.check_output(
            ["./gradlew", "clean", "build"],
            cwd=function_path,
        )


def get_function_url(provider: Provider, serverless_response, package_and_name, function_name):
    if provider == Provider.azure:
        return get_azure_function_url(serverless_response, package_and_name, function_name)

    aux2 = str(serverless_response.decode("UTF-8")).split("\n")
    for line in aux2:
        if package_and_name in line:
            return line.split()[2]

    return None


def get_azure_function_url(serverless_response, package_and_name, function_name):

    aux2 = str(serverless_response.decode("UTF-8")).split("\n")

    for line in aux2:
        if "Error" in aux2:
            return None

    config = read_conf()
    function_name = config["azureFunctions"][function_name]["function"].lower()
    return "https://" + function_name + ".azurewebsites.net/api/" + package_and_name
