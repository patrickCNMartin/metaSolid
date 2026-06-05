import ollama

model_name = "qwen:v1.0"
prompt = "Give me 5 synonyms for the word 'fast'."

print("Generating response...\n")

# Add stream=True to the request
response = ollama.chat(model=model_name, messages=[
    {'role': 'user', 'content': prompt}
], stream=True)

# Iterate through the stream as tokens are generated
for chunk in response:
    print(chunk['message']['content'], end='', flush=True)

print("\n\nDone!")