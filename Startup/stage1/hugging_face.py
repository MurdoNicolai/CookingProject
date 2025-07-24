#!/usr/bin/env python
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
def extract_title(filename):
    """Reads a text file and returns its title"""


    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    with open("example_recipes/" + filename, 'r', encoding='utf-8') as file:
        recipe_text = file.readlines()

    prompt = f"Extract or create a recipe title for the following text, it must be a recipe title:\n\n{recipe_text}"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )
    outputs = model.generate(**inputs, max_new_tokens=20)
    title = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("Generated Title:", title)

def extract_directions(filename):
    """Reads a text file and returns its title"""


    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    with open("example_recipes/" + filename, 'r', encoding='utf-8') as file:
        recipe_text = file.read()

    prompt = f"What are the directions of the folling recipe? Make a readable list out of them, only including directions:\n\n{recipe_text}"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=5120
    )
    outputs = model.generate(**inputs, max_new_tokens=1000)
    directions = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(directions)

# Example usage
# extract_title("recipe 3.txt")
extract_directions("recipe 6.txt")


