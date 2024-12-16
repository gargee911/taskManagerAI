file = "llm_task_input_output.json"
from huggingface_hub import login
login(token="hf_login_token")

import pandas as pd
import json

# Load JSON data from a file
with open("llm_task_input_output.json", "r") as file:
    json_data = json.load(file)

# Convert JSON data to a DataFrame
data = pd.json_normalize(json_data)

print(data)

print(data.columns)

data["text"] = data[["Input", "Instruction", "Output"]].apply(lambda x: "Below is an instruction that describes a task,paired with an input that provides further context. Write a response that appropriately completes the request. "+"###Instruction: " + x["Instruction"] + " " + "### Input:" + x["Input"] + " ###Response"+ x["Output"], axis=1)

print(data['text'][0])

import torch
from datasets import load_dataset, Dataset
from peft import LoraConfig, AutoPeftModelForCausalLM, prepare_model_for_kbit_training, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig, TrainingArguments
from trl import SFTTrainer
import os
from transformers import BitsAndBytesConfig

data = Dataset.from_pandas(data)

MODEL_ID = "gpt-3.5-turbo"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,    #load in 8 bit as well
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
)

#quantization
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb_config, device_map='auto')
model.config.use_cache=False
model.config.disable_exllama=True
model.config.pretraining_tp=1
model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

#QLORA
peft_config = LoraConfig(r=32, lora_alpha=16, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM", target_modules=["q_proj","v_proj"])
#peft-optimized model
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

import wandb
wandb.login(key="your_login_key")

data

training_arguments = TrainingArguments(
        output_dir='training_output',
        per_device_train_batch_size=8,
        gradient_accumulation_steps=1,
        optim="paged_adamw_8bit",
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        save_strategy="epoch",
        logging_steps=100,
        num_train_epochs=100,
        max_steps=400,
        fp16=True,
        push_to_hub=False,
        report_to="wandb"
)


trainer = SFTTrainer(
        model=model,
        train_dataset=data,
        peft_config=peft_config,
        dataset_text_field="text",
        args=training_arguments,
        tokenizer=tokenizer,
        packing=False,
        max_seq_length=512
)

trainer.train()

new_model="gargee-llama3b"
trainer.save_model(new_model)

hf_name = 'gargeekate123'
model_id = hf_name + "/" + "gargee-llama3b"
from huggingface_hub import HfApi

api = HfApi()
model_repo_name = "llama3bGargee"  # Format of Input  <Profile Name > / <Model Repo Name>

#Create Repo in Hugging Face
api.create_repo(repo_id=model_repo_name)

#Upload Model folder from Local to HuggingFace
api.upload_folder(
    folder_path=new_model,
    repo_id=model_repo_name
)

tokenizer.push_to_hub(model_repo_name)

#Inference

from peft import AutoPeftModelForCausalLM
from transformers import GenerationConfig
from transformers import AutoTokenizer
import torch
tokenizer = AutoTokenizer.from_pretrained("gargee-llama3b")

inputs = tokenizer("""###Instruction: Create a json block for this prompt and show in the following format and  Please do not add any explanation and show
 only json ### Input:Add a reminder for tomorrow 5 pm to visit the doctor ###Response: """, return_tensors="pt").to("cuda")

model = AutoPeftModelForCausalLM.from_pretrained(
    "gargee-llama3b",
    low_cpu_mem_usage=True,
    return_dict=True,
    torch_dtype=torch.float16,
    device_map="cuda")

generation_config = GenerationConfig(
    do_sample=True,
    top_k=1,
    temperature=0.6,
    max_new_tokens=100,
    pad_token_id=tokenizer.eos_token_id
)

print("/n Post-training Input - " + inputs)

import time
st_time = time.time()
outputs = model.generate(**inputs, generation_config=generation_config)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
print("/n")
print(time.time()-st_time)



#data_df1=pd.read_csv("/content/data.csv")
#data_df1 = data_df1.rename(columns={"""Below is an instruction that describes a task.
#Write a response that appropriately completes the request.\n### Instruction: Create a json block for this prompt
#'show me red nike shoes above Rs. 2000' and show in the following format.\n### Response: "{ \"prompt\":\
#"show me red nike shoes above Rs. 2000\", \u201caction_intent\u201d: \u201csearch\u201d, \u201cfilters\u201d:
#{ \"category_name\":\"Shoes\", \"brand_name\":\"Nike\", \"price_min\": \"2000\", \"price_max\": \"10000000\", \"provider_name\": \"\", \u201cquery_entity_type\u201d: \u201cproduct\u201d, \u201ccolour\u201d: \u201cred\u201d,
# \u201csize\u201d : \u201c\u201d } }"''': 'text'})
