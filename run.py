import os
import subprocess
from datetime import datetime

###Machine specific settings
path_to_main  = "/home/jvroig/Dev/llama.cpp"
model_basedir = "/run/media/jvroig/Data/VMShared/LLMs/llama/"
n_threads     = [ "8" ]
#n_threads     = [ "4", "6", "8", "10", "12" ]
model_base    = "llama-2-"
model_ext     = ".gguf"

####General settings - do not edit
executable        = "main"
output_basedir    = "results/output/"
error_basedir     = "results/perf/"
log_basedir       = "results/log/"
log_filename      = "run_" + datetime.now().strftime('%Y-%m-%d_%Hh%Mm') + ".txt"
max_input_tokens  = "1408"
max_output_tokens = "512"

###Experiment batch settings
# models = ["7b-chat", "13b-chat"]
# quants = ["q4_K", "q5_K", "q8", "f16"]
# temps  = ["0.1", "0.6", "1.0"]
models = ["7b-chat"]
quants = ["q4_K"]
temps  = ["0.6"]

prompt_domains = ["Business_Technical_Creative_Writing", 
                  "Sentiment_Analysis"]

prompt_types = ["LL",
                "LS",
                "SL",
                "SS"]

prompt_range = 3
prompt_runs = 5 #how many times each prompt (domain+type+num) is repeated


os.makedirs(os.path.dirname(log_basedir), exist_ok=True)
with open(log_basedir+log_filename, "a") as log_file:
    log_file.write("*******************\n")
    log_file.write("Experiment Settings:\n")
    log_file.write(f"Models: {str(models)}\n")
    log_file.write(f"Quants: {str(quants)}\n")
    log_file.write(f"Temps: {str(temps)}\n")
    log_file.write(f"Threads: {str(n_threads)}\n")
    log_file.write(f"Max Input Tokens: {str(max_input_tokens)}\n")
    log_file.write(f"Max Output Tokens: {str(max_output_tokens)}\n")
    log_file.write(f"Prompt Domains: {str(prompt_domains)}\n")
    log_file.write(f"Prompt Types: {str(prompt_types)}\n")
    log_file.write(f"Prompt Range: {str(prompt_range)}\n")
    log_file.write(f"Prompt Runs: {str(prompt_runs)}\n")
    log_file.write("-------------------\n")

for model_name in models:
    for quant in quants:
        for temp in temps:
            for threads in n_threads:
                for prompt_domain in prompt_domains:
                    for prompt_type in prompt_types:
                        for i in range(1, prompt_range+1):

                            prompt_file = "PT-" + prompt_type + f"{i:02}" + ".txt"
                            data_dir    = "data/" + prompt_domain + "/"

                            #Retreive prompt from prompt file
                            os.makedirs(os.path.dirname(data_dir + prompt_file), exist_ok=True)

                            #end the loop if the prompt file does not exist. This can happen because our prompt domains 
                            #   don't necessarily have the same quantity of prompts for each prompt type.
                            if os.path.isfile(data_dir+prompt_file) == False: break

                            with open(data_dir+prompt_file, "r") as f:
                                prompt = f.read()

                            # print("Prompt retrieved! Prompt:")
                            # print("***************************")
                            # print(prompt)
                            # print("***************************")

                            for run in range(1, prompt_runs + 1):
                                stdout = []

                                output_dir  = output_basedir + prompt_domain + "/" + model_base + model_name + "-" + quant + "/temp" + temp + "/threads" + threads + "/" + f"run{str(run)}/"
                                error_dir   = error_basedir + prompt_domain + "/" + model_base + model_name + "-" + quant + "/temp" + temp + "/threads" + threads + "/" + f"run{str(run)}/"
                                os.makedirs(os.path.dirname(output_dir + prompt_file), exist_ok=True)
                                os.makedirs(os.path.dirname(error_dir + prompt_file), exist_ok=True)

                                model_dir = model_base + model_name + "/"
                                model = model_base + model_name + "-" + quant + model_ext
                                model = model_basedir + model_dir + model

                                stdout.append("*******************")
                                stdout.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                stdout.append(f"Now running: {model} Temperature: {temp} Threads: {threads}")
                                stdout.append(f"Prompt Domain: {prompt_domain} Prompt file: {prompt_file} Run: {str(run)}")
                                
                                print(stdout[0])
                                print(stdout[1])
                                print(stdout[2])
                                print(stdout[3])

                                command = [f"{path_to_main}/{executable}", 
                                        "-m", model, 
                                        "-t", threads, 
                                        "-n", max_output_tokens,
                                        "-c", max_input_tokens,
                                        "--log-disable",
                                        "--prompt", prompt,]
                                
                                #print(command)
                                with open(output_dir+prompt_file, "w") as stdout_file, open(error_dir+prompt_file, "w") as stderr_file:
                                    process = subprocess.Popen(
                                        command,
                                        stdout=stdout_file,  # results go to the results file for human review
                                        stderr=stderr_file,  # raw perf data go to our stderr_file (llama.cpp pipes perf data to stderr),
                                        text=True
                                    )
                                    process.wait()

                                stdout.append("Done!")
                                stdout.append("-------------------")
                                print(stdout[4])
                                print(stdout[5])

                                with open(log_basedir+log_filename, "a") as log_file:
                                    log_file.write(stdout[0] + "\n")
                                    log_file.write(stdout[1] + "\n")
                                    log_file.write(stdout[2] + "\n")
                                    log_file.write(stdout[3] + "\n")
                                    log_file.write(stdout[4] + "\n")
                                    log_file.write(stdout[5] + "\n")

print("Done!")