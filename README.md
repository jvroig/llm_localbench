# llm_localbench
Python infrastructure for benchmarking LLMs.

##Running the benchmark - run.py
The **run.py** file executes the benchmark. This is designed for running local LLMs through llama.cpp. A working llama.cpp executable is necessary (and not provided by this repo).

There are configuration items inside of the script that determines what will be run and how, including the path of executables, models, data, and where to dump the results.


*[WIP: These configurations will soon be improved and spun out of run.py]*


##Non-local executions - Amazon SageMaker - sagemaker_run.py
There is preliminary support for benchmarking through AWS/SageMaker, necessary for huge models that simply can't feasibly be run on local machines (for example, full-precision Llama 2 70B and larger).


##Consolidating Results - results_to_csv.py
The benchmarks (whether *run.py* or *sagemaker_run.py*) create tons of results and log data. To consolidate these into a more human-friendly, summarized form, *results_to_csv.py* can be used.

There are settings inside of this file that are needed to be set correctly:
- *path_to_data*: where the test data is
- *path_to_results*: where the result data can be found
- *output_csv*: what to name the output file for response data
- *perf_csv*: what to name the outpuf file for the performance data
    