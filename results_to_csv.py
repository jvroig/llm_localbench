import os
import re
import csv
import subprocess
from datetime import datetime


###############
#General Config
path_to_data    = "data"
path_to_results = "/mnt/AData/VMShared/llm_localbench_results/EC2_Trial1"
output_csv      = "results_output.csv"
perf_csv        = "results_perf.csv"

#####################################
#Get all prompts from the data folder
prompts = {}
subfolders = [f.name for f in os.scandir(path_to_data) if f.is_dir()]
for subfolder in subfolders:
    prompts[subfolder] = {}
    prompt_files = [f for f in os.listdir(path_to_data + os.sep + subfolder) if f.endswith(".txt")]
    for prompt_file in prompt_files:
        file_name = os.path.splitext(prompt_file)[0]
        prompt_text = ''
        with open(path_to_data + os.sep + 
                  subfolder + os.sep + 
                  prompt_file) as f:
            prompt_text = f.read()
        prompts[subfolder][file_name] = prompt_text

###################################
#Get output from the results folder
output = {} #raw results from the experiment
results_folder = path_to_results + os.sep + 'results' + os.sep + 'output'
domains = [f.name for f in os.scandir(results_folder) if f.is_dir()]
for domain in domains:
    output[domain] = {}
    domain_folder = results_folder + os.sep + domain
    families = [f.name for f in os.scandir(domain_folder) if f.is_dir()]
    for family in families:
        family_folder = domain_folder + os.sep + family
        models = [f.name for f in os.scandir(family_folder) if f.is_dir()]
        for model in models:
            output[domain][model] = {}
            model_folder = family_folder + os.sep + model
            temps = [f.name for f in os.scandir(model_folder) if f.is_dir()]
            for temp in temps:
                output[domain][model][temp] = {}
                temp_folder = model_folder + os.sep + temp
                threads = [f.name for f in os.scandir(temp_folder) if f.is_dir()]
                for thread in threads:
                    output[domain][model][temp][thread] = {}
                    thread_folder = temp_folder + os.sep + thread
                    runs = [f.name for f in os.scandir(thread_folder) if f.is_dir()]
                    print("Inside threads!")
                    print(thread)
                    print(runs)
                    for run in runs:
                        output[domain][model][temp][thread][run] = {}
                        run_folder = thread_folder + os.sep + run
                        output_files = [f for f in os.listdir(run_folder) if f.endswith(".txt")]
                        for output_file in output_files:
                            prompt_type = os.path.splitext(output_file)[0]
                            output_text = ''
                            with open(run_folder + os.sep + output_file) as f:
                                output_text = f.read()
                            #remove original prompt from output_text
                            answer = output_text.replace(prompts[domain][prompt_type], "")
                            output[domain][model][temp][thread][run][prompt_type] = answer


############################
#Write results to Output CSV
csv_data = [
    ['Model', 'Domain', 'Prompt#', 'Temp', 'Threads', 'Run', 'Prompt Text', 'Response Text' ]
]

domains = list(output.keys())
for domain in domains:
    models = list(output[domain].keys())
    for model in models:
        temps = list(output[domain][model].keys())
        for temp in temps:
            threads = list(output[domain][model][temp].keys())
            for thread in threads:
                runs = list(output[domain][model][temp][thread].keys())
                for run in runs:
                    prompt_types = list(output[domain][model][temp][thread][run].keys())
                    for prompt_type in prompt_types:
                        response_text = output[domain][model][temp][thread][run][prompt_type] 
                        prompt_text   = prompts[domain][prompt_type]
                        csv_data.append([model, domain, prompt_type, temp[4:], thread[7:], run[3:], prompt_text, response_text])

with open(output_csv, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(csv_data)



#################################
#Get perf from the results folder
perf           = {} #raw performance logs from the experiment
perf_lines     = 10
results_folder = path_to_results + os.sep + 'results' + os.sep + 'perf'
domains = [f.name for f in os.scandir(results_folder) if f.is_dir()]
for domain in domains:
    perf[domain] = {}
    domain_folder = results_folder + os.sep + domain
    families = [f.name for f in os.scandir(domain_folder) if f.is_dir()]
    for family in families:
        family_folder = domain_folder + os.sep + family
        models = [f.name for f in os.scandir(family_folder) if f.is_dir()]
        for model in models:
            perf[domain][model] = {}
            model_folder = family_folder + os.sep + model
            temps = [f.name for f in os.scandir(model_folder) if f.is_dir()]
            for temp in temps:
                perf[domain][model][temp] = {}
                temp_folder = model_folder + os.sep + temp
                threads = [f.name for f in os.scandir(temp_folder) if f.is_dir()]
                for thread in threads:
                    perf[domain][model][temp][thread] = {}
                    thread_folder = temp_folder + os.sep + thread
                    runs = [f.name for f in os.scandir(thread_folder) if f.is_dir()]
                    for run in runs:
                        perf[domain][model][temp][thread][run] = {}
                        run_folder = thread_folder + os.sep + run
                        perf_files = [f for f in os.listdir(run_folder) if f.endswith(".txt")]
                        for perf_file in perf_files:
                            prompt_type = os.path.splitext(perf_file)[0]
                            perf_text = ''
                            with open(run_folder + os.sep + perf_file) as f:
                                perf_data = f.readlines()[-perf_lines:]
                            perf[domain][model][temp][thread][run][prompt_type] = perf_data


############################
#Write results to Perf CSV
csv_data = [
    ['Model', 'Domain', 'Prompt#', 'Temp', 'Threads', 'Run', 'Mem Required (MB)', 'Sample Time (tokens/sec)', 'Input Tokens', 'Prompt Eval Time (tokens/sec)', 'Output Tokens', 'Eval Time (tokens/sec)', 'Total Time (ms)']
]

domains = list(output.keys())
for domain in domains:
    models = list(output[domain].keys())
    for model in models:
        temps = list(output[domain][model].keys())
        for temp in temps:
            threads = list(output[domain][model][temp].keys())
            for thread in threads:
                runs = list(output[domain][model][temp][thread].keys())
                for run in runs:
                    prompt_types = list(output[domain][model][temp][thread][run].keys())
                    for prompt_type in prompt_types:
                        perf_data = perf[domain][model][temp][thread][run][prompt_type] 

                        mem_required = re.search(r'[\d.]+', perf_data[0]).group() #FIXME: this is wrong when using CUDA
                        sample_time = re.search(r'[\d.]+', perf_data[6].split("(")[1].split(",")[1]).group()
                        input_tokens = re.search(r'[\d.]+', perf_data[7].split("/")[1]).group()
                        prompt_eval_time = re.search(r'[\d.]+', perf_data[7].split("(")[1].split(",")[1]).group()
                        output_tokens = re.search(r'[\d.]+', perf_data[8].split("/")[1]).group()
                        eval_time_match = re.search(r'[\d.]+', perf_data[8].split("(")[1].split(",")[1])
                        if eval_time_match: eval_time = eval_time_match.group()
                        else: eval_time = 0 #special handling for eval_time needed, because if the LLM does not produce an output, llama.cpp will log it as "inf" tokens per second
                        total_time = re.search(r'[\d.]+', perf_data[9]).group()
                        csv_data.append([model, domain, prompt_type, temp[4:], thread[7:], run[3:], 
                                         mem_required, sample_time, input_tokens, prompt_eval_time, output_tokens, eval_time, total_time])

with open(perf_csv, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerows(csv_data)
