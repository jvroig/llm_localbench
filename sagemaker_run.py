import os
import json
from datetime import datetime

import boto3
from botocore.config import Config
my_config = Config(region_name = 'us-east-2')

###Machine specific settings
path_to_main  = "/home/jvroig/Dev/llama.cpp"
#n_threads     = [ "4", "6", "8", "10", "12" ]
n_threads     = [ "8" ]
model_base    = "llama-2-"
model_ext     = ".gguf"
model_basedir = "/mnt/hgfs/VMShared/LLMs/llama/"

####General settings - do not edit
executable        = "main"
output_basedir    = "results/output/"
error_basedir     = "results/perf/"
log_basedir       = "results/log/"
log_filename      = "run_" + datetime.now().strftime('%Y-%m-%d_%Hh%Mm')
max_input_tokens  = "1408"
max_output_tokens = "512"

###Experiment batch settings
models = ["7b-chat", "13b-chat"]
quants = ["q4_K", "q5_K", "f16"]
#temps  = ["0.1", "0.6", "1.0"]
temps  = ["0.6"]
# prompt_domains = ["Business_Technical_Creative_Writing", 
#                   "Sentiment_Analysis"]

prompt_domains = [ 
                  "Business_Technical_Creative_Writing"]

# prompt_types = [
#     "LL",
#     "LS",
#     "SL",
#     "SS",
#     "AWS",
#     "TITLE",
#     "TAGS"
# ]

prompt_types = ["SL", "SS"]

prompt_range = 3

prompt_runs = 20 #how many times each prompt (domain+type+num) is repeated

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


#Sagemaker
endpoint_name = "jumpstart-dft-meta-textgeneration-llama-2-70b-f"

def query_endpoint(payload):
    client = boto3.client("sagemaker-runtime", config=my_config)
    response = client.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=json.dumps(payload),
        CustomAttributes="accept_eula=true",
    )
    response = response["Body"].read().decode("utf8")
    response = json.loads(response)
    return response


model_name = "sagemaker-llama-2-70b-chat"
quant = "f16"
threads = "default"
for temp in temps:
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
                    
                    output_dir  = output_basedir + prompt_domain + "/" + model_base + model_name + "-" + quant + "/temp" + temp + "/threads" + threads + "/" + f"run{str(run)}/"
                    error_dir   = error_basedir + prompt_domain + "/" + model_base + model_name + "-" + quant + "/temp" + temp + "/threads" + threads + "/" + f"run{str(run)}/"
                    os.makedirs(os.path.dirname(output_dir + prompt_file), exist_ok=True)
                    # os.makedirs(os.path.dirname(error_dir + prompt_file), exist_ok=True)

                    model_dir = model_base + model_name + "/"
                    model = model_base + model_name + "-" + quant + model_ext
                    model = model_basedir + model_dir + model

                    stdout = []
                    stdout.append("*******************")
                    stdout.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    stdout.append(f"Now running: {model_name} Temperature: {temp} Threads: {threads}")
                    stdout.append(f"Prompt file: {prompt_file} Run: {str(run)}")
                    
                    print(stdout[0])
                    print(stdout[1])
                    print(stdout[2])
                    print(stdout[3])

                    payload = {
                        "inputs": [[{"role": "user", "content": prompt}]], 
                        "parameters": {"max_new_tokens": int(max_output_tokens), "top_p": 0.9, "temperature": float(temp)}
                    }
                    result = query_endpoint(payload)[0]
                    answer = f"{result['generation']['content']}"


                    with open(output_dir+prompt_file, "w") as stdout_file:
                        stdout_file.write("Prompt:" + "\n")
                        stdout_file.write(prompt + "\n")
                        stdout_file.write("Response:" + "\n")
                        stdout_file.write(answer + "\n")

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
