from ResultController import *
from ConfigController import *

import subprocess
import os
import time

import xml.etree.ElementTree as ElementTree

from typing import Callable, List, Dict

TEST_FUNCTION = Callable[[List[str], str, List, str, str or Dict[str, str], ElementTree, float], str or None]


def run_test(args):
    test_number = args[1]

    if test_number == '1':
        run_test_fun(run_overhead_test, args)
    elif test_number == '2':
        run_test_fun(run_concurrency_test, args)
    elif test_number == '3':
        run_test_fun(run_container_reuse_test, args)
    elif test_number == '4':
        run_test_fun(run_payload_test, args)
    elif test_number == '5':
        run_test_fun(run_overhead_languages_test, args)
    elif test_number == '6':
        run_test_fun(run_memory_test, args)
    elif test_number == '7':
        run_test_fun(run_weight_test, args)


def run_test_fun(test_func: TEST_FUNCTION, args: List[str]):
    serverless_provider = args[0].lower()
    test_number = args[1]

    test = "T{0}".format(test_number)
    ts = int(time.time())
    files = []
    execution_time = ""

    print('Getting JMeter template...')
    template = get_template(test)

    if template is None:
        print('No template for test founded!')
        return None

    serverless_providers = get_all_providers(test) if serverless_provider == 'all' else [serverless_provider]

    for provider in serverless_providers:

        if not verify_test_provider(test, serverless_provider):
            print("The test is not specified for that provider")
            return None

        print('Updating Template for test...')
        function_url = get_function_url(serverless_provider, test)

        if function_url is None or function_url == "":
            print("No function deployed for test {0} on {1} provider".format(test, serverless_provider))
            continue

        test_execution_time = test_func(args, test, files, provider, function_url, template, ts)

        if test_execution_time is not None:
            execution_time = test_execution_time

    print('Calculate the result...')
    result_name = 'all' if serverless_provider == 'all' else serverless_provider
    result_controller(test_number, files, ts, result_name, execution_time)


def run_overhead_test(args: List[str], test: str, files: List, serverless_provider: str,
                      function_url: str,  template: ElementTree, ts: float) -> str or None:
    test_number = args[1]
    execution_time = args[2]
    print(args)

    if test_number != '1':
        return None

    update_t1_template(function_url, execution_time, template, test)
    file_name = get_output_file_name(ts, serverless_provider)
    run_jmeter(file_name, test, serverless_provider)
    # print(str(jmeter_result.decode('UTF-8')))

    file = (file_name, serverless_provider)
    files.append(file)

    return execution_time


def run_concurrency_test(args: List[str], test: str, files: List, serverless_provider: str,
                         function_url: str,  template: ElementTree, ts: float) -> str or None:
    min_concurrency = int(args[2])
    max_concurrency = int(args[3])
    concurrency_step = int(args[4])
    execution_time = args[5]

    files_provider = []
    for num_threads in range(min_concurrency, max_concurrency + 1, concurrency_step):
        update_t2_template(function_url, execution_time, template, test, num_threads)
        file_name = get_output_file_name(ts, serverless_provider)
        file_name_aux = file_name.split('.')
        file_name_final = create_final_file_name(file_name_aux[0], 'concurrency', str(num_threads), file_name_aux[1])
        jmeter_result = run_jmeter(file_name_final, test, serverless_provider)
        # print(str(jmeter_result.decode('UTF-8')))

        throughput = get_running_data(str(jmeter_result.decode('UTF-8')))

        file = (file_name_final, serverless_provider, num_threads, throughput)
        files_provider.append(file)
    files.append(files_provider)
    return execution_time


def run_container_reuse_test(args: List[str], test: str, files: List, serverless_provider: str,
                             function_url: str,  template: ElementTree, ts: float) -> str or None:
    test_number = args[1]
    min_wait_time = int(args[2])
    max_wait_time = int(args[3])
    time_step = int(args[4])
    execution_time = args[5]

    if test_number != '3':
        return None

    files_provider = []

    print('Getting JMeter template...')
    postfixed_test_number = "{0}_0".format(test_number)
    postfixed_test_name = "{0}_0".format(test)

    template = get_template(postfixed_test_number)

    if template is None:
        print('No template for test founded!')
        return None

    print('Updating Template for test...')

    update_t1_template(function_url, execution_time, template, postfixed_test_name)
    file_name = get_output_file_name(ts, serverless_provider)
    file_name_aux = file_name.split('.')
    file_name_final = "{0}-{1}.{2}".format(file_name_aux[0], 'preexecution', file_name_aux[1])

    run_jmeter(file_name_final, test, serverless_provider, "_0")

    print('Pre executions:')
    # print(str(jmeter_result.decode('UTF-8')))

    postfixed_test_number = "{0}_1".format(test_number)
    postfixed_test_name = "{0}_1".format(test)

    template = get_template(postfixed_test_number)

    if template is None:
        print('No template for test founded!')
        return None

    print('Updating Template for test...')

    for wait_time in range(min_wait_time, max_wait_time + 1, time_step):
        info_tet = "\nRun test in {0} after waiting {1} seconds!\n".format(serverless_provider, str(wait_time))
        print(info_tet)

        time.sleep(wait_time)

        update_t3_template(get_function_url(serverless_provider, test), template, postfixed_test_name)

        file_name = get_output_file_name(ts, serverless_provider)
        file_name_aux = file_name.split('.')
        file_name_final = create_final_file_name(file_name_aux[0], 'waittime', str(wait_time), file_name_aux[1])

        run_jmeter(file_name_final, test, serverless_provider, "_1")
        # print(str(jmeter_result.decode('UTF-8')))

        file = (file_name_final, serverless_provider, wait_time)
        files_provider.append(file)

    files.append(files_provider)
    return execution_time


def run_payload_test(args: List[str], test: str, files: List, serverless_provider: str,
                     function_url: str,  template: ElementTree, ts: float) -> str or None:

    execution_time = args[2]
    payload_size = get_payload_size(test)
    files_provider = []

    for pay_size in payload_size:
        function_url_with_pay_size = append_query_parameter(function_url, str(pay_size))
        update_t1_template(function_url_with_pay_size, execution_time, template, test)
        file_name = get_output_file_name(ts, serverless_provider)
        file_name_aux = file_name.split('.')

        file_name_final = create_final_file_name(file_name_aux[0], 'payloadSize', str(pay_size), file_name_aux[1])
        run_jmeter(file_name_final, test, serverless_provider)
        # print(str(jmeter_result.decode('UTF-8')))

        file = (file_name_final, serverless_provider, pay_size)
        files_provider.append(file)

    files.append(files_provider)
    return execution_time


def run_overhead_languages_test(args: List[str], test: str, files: List, serverless_provider: str,
                                functions: Dict[str, str], template: ElementTree, ts: float) -> str or None:
    execution_time = args[2]

    for programming_lang, url in functions.items():
        if url is None or url == "":
            print("No function in {0} for test {1} on {2} provider"
                  .format(programming_lang, test, serverless_provider))
            return None

        else:
            update_t1_template(url, execution_time, template, test)
            file_name = get_output_file_name(ts, serverless_provider)
            file_name_aux = file_name.split('.')

            file_name_final = create_final_file_name(
                file_name_aux[0], 'Pro_Language', programming_lang, file_name_aux[1]
            )

            run_jmeter(file_name_final, test, serverless_provider)
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, programming_lang)
            files.append(file)
    return execution_time


def run_memory_test(args: List[str], test: str, files: List, serverless_provider: str,
                    functions: Dict[str, str], template: ElementTree, ts: float) -> str or None:
    execution_time = args[2]

    for func_mem, url in functions.items():
        if url is None or url == "":
            print("No function with {0}Mb of memory for test {1} on {2} provider"
                  .format(func_mem, test, serverless_provider))
            return None

        else:
            update_t1_template(url, execution_time, template, test)
            file_name = get_output_file_name(ts, serverless_provider)
            file_name_aux = file_name.split('.')

            file_name_final = create_final_file_name(file_name_aux[0], 'Memory', func_mem, file_name_aux[1])

            run_jmeter(file_name_final, test, serverless_provider)
            # print(str(jmeter_result.decode('UTF-8')))

            file = (file_name_final, func_mem)
            files.append(file)

    return execution_time


def run_weight_test(args: List[str], test: str, files: List, serverless_provider: str,
                    function_url: str, template: ElementTree, ts: float) -> str or None:
    execution_time = args[2]

    weights = get_weights(test)

    files_provider = []

    for weight in weights:
        function_url_appended = append_query_parameter(function_url, str(weight))
        update_t1_template(function_url_appended, execution_time, template, test)
        file_name = get_output_file_name(ts, serverless_provider)
        file_name_aux = file_name.split('.')
        file_name_final = create_final_file_name(file_name_aux[0], 'fib', str(weight), file_name_aux[1])

        run_jmeter(file_name_final, test, serverless_provider)
        # print(str(jmeter_result.decode('UTF-8')))

        file = (file_name_final, serverless_provider, weight)
        files_provider.append(file)

    files.append(files_provider)
    return execution_time


def get_template(test: str) -> ElementTree:
    return ElementTree.ElementTree(file=get_template_path(test))


def get_template_path(test: str) -> str:
    config = read_conf()
    return config['jMeterTemplates'][test]


def get_function_url(serverless_provider: str, test: str):
    config = read_conf()
    return config['functionsURL'][serverless_provider][test]


def create_final_file_name(file_name: str, test_name: str, addition: str, ending: str) -> str:
    return "{0}-{1}_{2}.{3}".format(file_name, test_name, addition, ending)


def append_query_parameter(url: str, appendix: str) -> str:
    return "{0}?n={1}".format(url, appendix)


def update_t1_template(url: str, execution_time: str, template: ElementTree, test: str):
    root = template.getroot()

    for elem in template.iter():
        name = elem.attrib.get('name')
        if name == 'ThreadGroup.duration':
            elem.text = execution_time
        elif name == 'HTTPSampler.path':
            elem.text = url

    write_file(root, test)


def update_t2_template(url: str, execution_time: str, template: ElementTree, test: str, n_threads: int):
    root = template.getroot()

    for elem in template.iter():
        name = elem.attrib.get('name')
        if name == 'ThreadGroup.duration':
            elem.text = execution_time
        elif name == 'HTTPSampler.path':
            elem.text = url
        elif name == 'ThreadGroup.num_threads':
            elem.text = str(n_threads)

    write_file(root, test)


def update_t3_template(url, template, test):
    root = template.getroot()

    for elem in template.iter():
        if elem.attrib.get('name') == 'HTTPSampler.path':
            elem.text = url

    write_file(root, test)


def write_file(root: ElementTree, test: str):
    tree = ElementTree.ElementTree(root)
    tree.write(get_template_path(test))


def get_output_file_name(ts: float, serverless_provider: str):
    return "{0}{1}.jtl".format(serverless_provider, str(ts))


def get_output_file(test: str, file_name: str) -> str:
    config = read_conf()
    file_path = "{0}/{1}/{2}".format(str(os.getcwd()), str(config['jMeterResultsPath'][test]), file_name)
    print('Generated file with results:' + file_path)
    return file_path


def get_jmeter_path() -> str:
    config = read_conf()
    return config['jMeterPath']


def run_jmeter(file_name_final: str, test: str, serverless_provider: str, template_path_appendix: str = ""):
    template_path = get_template_path(test + template_path_appendix)
    output_file = get_output_file(test, file_name_final)
    jmeter_path = get_jmeter_path()

    print("Running test {0} in the {1} on JMeter...".format(test, serverless_provider))
    final_template_path = "{0}/{1}".format(os.getcwd(), template_path)
    # print(final_template_path, output_file, jmeter_path)
    aux = subprocess.check_output(
        ['sh', 'jmeter', '-n', '-t', final_template_path, '-l', output_file, '-f'], cwd=jmeter_path
    )
    return aux


def get_all_providers(test: str) -> List[str]:
    config = read_conf()
    providers = config['providers'][test]
    # print('-----------', providers)
    return providers


def get_payload_size(test: str) -> List[int]:
    config = read_conf()
    test_number_f = "{0}PayloadSize".format(test)
    return config[test_number_f]


def get_weights(test: str) -> List[int]:
    config = read_conf()
    test_number_f: str = "{0}Weights".format(test)
    return config[test_number_f]


def verify_test_provider(test: str, provider: str) -> bool:
    config = read_conf()
    providers = config['providers'][test]

    if provider in providers:
        return True
    return False


def get_running_data(result_data: str) -> str:
    aux = result_data.split('\n')

    for line in aux:
        if 'summary =' in line:
            info = line.split('/')
            return info[0].split(' ')[-1]
