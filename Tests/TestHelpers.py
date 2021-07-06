import subprocess
import os

import xml.etree.ElementTree as ElementTree

from typing import List

from ConfigController import read_conf


def get_function_url(serverless_provider: str, test: str):
    config = read_conf()
    return config["functionsURL"][serverless_provider][test]


def create_final_file_name(file_name: str, test_name: str, addition: str, ending: str) -> str:
    return "{0}-{1}_{2}.{3}".format(file_name, test_name, addition, ending)


def append_query_parameter(url: str, appendix: str) -> str:
    return "{0}?n={1}".format(url, appendix)


def update_t1_template(url: str, execution_time: str, template: ElementTree, file_path: str):
    root = template.getroot()

    for elem in template.iter():
        name = elem.attrib.get("name")
        if name == "ThreadGroup.duration":
            elem.text = execution_time
        elif name == "HTTPSampler.path":
            elem.text = url

    write_file(root, file_path)


def update_t2_template(url: str, execution_time: str, template: ElementTree, file_path: str, n_threads: int):
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


def write_file(root: ElementTree, file_path: str):
    tree = ElementTree.ElementTree(root)
    tree.write(file_path)


def get_output_file_name(ts: float, serverless_provider: str):
    return "{0}{1}.jtl".format(serverless_provider, str(ts))


def get_output_file(test: str, file_name: str) -> str:
    config = read_conf()
    file_path = "{0}/{1}/{2}".format(str(os.getcwd()), str(config["jMeterResultsPath"][test]), file_name)
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


def get_payload_size(test: str) -> List[int]:
    config = read_conf()
    test_number_f = "{0}PayloadSize".format(test)
    return config[test_number_f]


def get_weights(test: str) -> List[int]:
    config = read_conf()
    test_number_f: str = "{0}Weights".format(test)
    return config[test_number_f]


def get_running_data(result_data: str) -> str:
    aux = result_data.split("\n")

    for line in aux:
        if "summary =" in line:
            info = line.split("/")
            return info[0].split(" ")[-1]


def get_jmeter_result_path(test_number):
    config = read_conf()
    file_path = str(config["jMeterResultsPath"]["T" + test_number])
    return file_path
