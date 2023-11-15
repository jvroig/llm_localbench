import os
import subprocess

#FIXME: Turn config into a YAML file 
from config import *

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
                            if os.path.isfile(data_dir+prompt_file) == False: continue

                            with open(data_dir+prompt_file, "r") as f:
                                prompt = f.read()

                            # print("Prompt retrieved! Prompt:")
                            # print("***************************")
                            # print(prompt)
                            # print("***************************")

                            for run in range(1, prompt_runs + 1):
                                stdout = []

                                output_dir  = output_basedir + prompt_domain + "/" + model_name + "-" + quant + "/temp" + temp + "/threads" + threads + "/" + f"run{str(run)}/"
                                error_dir   = error_basedir + prompt_domain + "/" + model_name + "-" + quant + "/temp" + temp + "/threads" + threads + "/" + f"run{str(run)}/"
                                os.makedirs(os.path.dirname(output_dir + prompt_file), exist_ok=True)
                                os.makedirs(os.path.dirname(error_dir + prompt_file), exist_ok=True)

                                model = model_name + "-" + quant + model_ext
                                model = model_basedir + model

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
                                        "-ngl", n_gpu_layers,
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
