# Overview
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Expandable command-line software tool to benchmark serverless platforms from Amazon, Google, Microsoft and IBM.

The seven deﬁned tests cover scalability (latency and throughput), the effect of allocated memory, the performance for CPU-bound cases, the impact of payload size, the inﬂuence of the programming language, resource management (e.g., reuse of containers), and overall platform overhead.


**This project is base on the [Benchmarking Serverless Computing Platforms](https://link.springer.com/content/pdf/10.1007/s10723-020-09523-1.pdf) paper by Horacio Martins, Filipe Araujo and Paulo Rupino da Cunha**

They were so generous to provide the code for the benchmarking on [GitHub](https://github.com/hjmart93/ServerlessBenchmark).
This code is working perfectly fine, but I had problems to understand it, so I improved a couple of things without changing the concept nor the behaviour of the tool.

Therefor I changed the following:

1. Update to python 3
2. Update all the lambda functions (including gradle, java, node etc. )
3. Added auto build to the `deploy` functionality of the Benchmarking tool   
4. Add a pipfile to install all dependencies (simply run `pipenv install` to install all dependencies)
5. Add type hints
6. Refactor code to be less redundant and more test case oriented with a small amount of shared helper functions
7. Use `.format` instead of string aggregation
8. Added Black for codestyle
9. Gave the tests a proper name in the file system and in the config
10. Improved this readme
11. a lot of smaller bugfixes, typo fixes and other stuff

# Contribute

I will add more stuff to this repository in the following month. If you want to contribute to my fork create a Pull Request.
I will look into it as fast as I can. Please just stick to the codestyle.

# How to

## Install

Make sure, that pipenv and python 3 is installed on your system.  
Run `pipenv install` in the root of this directory.

## Start a test

First you need to creat a `conf.json` file in the root of this repository. You can copy/rename the `example_conf.json` for that.
Run a test by executing the AppInterface with python 3.

The most important arguments are:

1. `-s or --suite` to define, which test suite should be executed
2. `-p or --provider` to define the provider. Default is all providers
3. `-d or --deploy` to deploy the functions for the test suite
4. `-t or --test` to execute the test itself   
4. `-r or --remove` to remove the deployed functions for the test suite

This would deploy, run and remove the first test, which is the Overhead Test on AWS:

`python ServerlessBenchmarkAppInterface.py -t -d -r -p aws -s 1 90`

The last parameter is the execution time. It is test specific for the Overhead Test.
Other test specific arguments are explained below

## Other Tests and their arguments

## Overhead

```
ServerlessBenchmarkAppInterface.py -s 1 -o execution_time
```

where execution_time is the amount of time the test should last.

## Concurrency Test

```
ServerlessBenchmarkAppInterface.py -s 2 -o min_concurrency max_concurrency concurrency_step level_concurrency_execution_time
```

where min_concurrency is the starting level of concurrency;  
max_concurrency is the final level;  
concurrency_step is the step, e.g., from 1 to 30 step 2, would run the test with concurrence 1, 3, 5, etc. up to 29;  
and level_concurrency_execution_time is the time the tool spends on each concurrency level.  

## Container Reuse Test

```
ServerlessBenchmarkAppInterface.py -s 3 -o min_wait_time max_wait_time time_step pre_execution_time
```

where min_wait_time is the first interval of waiting time between invocations;  
max_wait_time is the last interval;  
time_step is the step increment from the minimum to the maximum;  
and re_execution_time is a warm-up time with invocations before the actual test, to enable the platform to prepare containers.  

## Payload Test

```
ServerlessBenchmarkAppInterface.py -s 4 -o execution_time
```

where execution_time is the amount of time the test should last.


## Overhead Language Test

```
ServerlessBenchmarkAppInterface.py -s 5 -o execution_time
```

where execution_time is the amount of time the test should last.

## Memory Test

```
ServerlessBenchmarkAppInterface.py -s 6 -o execution_time
```

where execution_time is the amount of time the test should last.

## Weight Test

```
ServerlessBenchmarkAppInterface.py -s 7 -o execution_time
```

where execution_time is the amount of time the test should last.
       
