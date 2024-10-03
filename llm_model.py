# llm_model.py

import warnings
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load the tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2', use_fast=False)
model = GPT2LMHeadModel.from_pretrained('gpt2')

def generate_response(input_text):
    # Tokenize the input text
    inputs = tokenizer.encode(input_text, return_tensors='pt', clean_up_tokenization_spaces=True)

    # Generate a response using the model
    outputs = model.generate(inputs, max_length=50, num_return_sequences=1)

    # Decode the generated tokens to get the response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return response
