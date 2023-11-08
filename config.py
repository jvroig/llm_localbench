from datetime import datetime

###Machine specific settings
path_to_main  = "/home/jvroig/Dev/llama.cpp"
#n_threads     = [ "4", "6", "8", "10", "12" ]
n_threads     = [ "8" ]
n_gpu_layers  = "20"
model_ext     = ".gguf"
model_basedir = "/mnt/AData/VMShared/LLMs/"

###General settings - do not edit
executable        = "main"
output_basedir    = "results/output/"
error_basedir     = "results/perf/"
log_basedir       = "results/log/"
log_filename      = "run_" + datetime.now().strftime('%Y-%m-%d_%Hh%Mm')
max_input_tokens  = "1408"
max_output_tokens = "512"

###Experiment batch settings
# models = [
#     "llama-2/llama-2-7b-chat", 
#     "llama-2/llama-2-13b-chat", 
#     "mistral/mistral-7b-instruct",
#     "falcon/falcon-7b-instruct"
# ]
# quants = ["q4_K", "q5_K", "q8_0", "f16"]
# temps  = ["0.1", "0.6", "1.0"]

models = [
    "mistral/mistral-7b-instruct",
]
quants = ["q4_K"]
temps  = ["0.6"]

prompt_domains = ["Business_Technical_Creative_Writing", 
                  "Sentiment_Analysis",
                  "Cloud"]

prompt_types = [
    "LL",
    "LS",
    "SL",
    "SS",
    "AWS",
    "TITLE",
    "TAGS"
]

prompt_range = 12
prompt_runs = 20 #how many times each prompt (domain+type+num) is repeated
