#!/usr/bin/env python
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
"""Reads a text file and returns its title"""
model_name = "./flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
line = "* 3 tablespoons palm or light brown sugar"
prompt = f"Extract the ingredient name (the main food item, not the amount, or origin)\
    that appears in the following text.Only return the ingredient noun. Make sur it is the full ingredient when \
    the ingredient is comoposed of several words, or when there is a specific form, color or description\
    If there are alternative ingredients (for example after an \"or\"), extract them the same way, seperated by a coma.\
    \n{line}"

prompt = f"{prompt}, when prompted with this prompt you return \"palm\" I would like the return to be \"palm, light brown sugar\". Return a new prompt in which the return is \"palm, light brown sugar\" and not \"palm\""
inputs = tokenizer(
    prompt,
    return_tensors="pt",
    truncation=True,
    max_length=512
)
outputs = model.generate(**inputs, max_new_tokens=20)
title = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(title)
