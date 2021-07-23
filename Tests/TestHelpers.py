import subprocess
import os

import xml.etree.ElementTree as ElementTree
from ConfigController import read_conf


def get_function_url(serverless_provider: str, test: str):
    config = read_conf()
    return config["functionsURL"][serverless_provider][test]


def append_query_parameter(url: str, appendix: str) -> str:
    return "{0}?n={1}".format(url, appendix)


def write_file(root: ElementTree, file_path: str):
    tree = ElementTree.ElementTree(root)
    tree.write(file_path)


def get_output_file(test: str, file_name: str) -> str:
    file_path = "{0}/{1}/{2}".format(str(os.getcwd()), get_jmeter_result_path(test), file_name)
    print("Generated file with results:" + file_path)
    return file_path


def get_jmeter_path() -> str:
    config = read_conf()
    return config["jMeterPath"]


def run_jmeter(
    file_name_final: str,
    test: str,
    serverless_provider: str,
    template_path: str,
):
    output_file = get_output_file(test, file_name_final)
    jmeter_path = get_jmeter_path()

    print("Running test {0} in the {1} on JMeter...".format(test, serverless_provider))
    # print(final_template_path, output_file, jmeter_path)
    aux = subprocess.check_output(
        ["sh", "jmeter", "-n", "-t", template_path, "-l", output_file, "-f"],
        cwd=jmeter_path,
    )
    return aux


def get_running_data(result_data: str) -> str:
    aux = result_data.split("\n")

    for line in aux:
        if "summary =" in line:
            info = line.split("/")
            return info[0].split(" ")[-1]


def get_jmeter_result_path(test: str):
    config = read_conf()
    return "{0}/{1}".format(str(config["jMeterResultsPath"]), test)
