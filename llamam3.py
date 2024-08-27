"""
Run Llama3 8B locally on Apple Silicon neural engine
"""

from mlx_lm import load, generate

# Define your model to import
model_name = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"

# Loading model
model, tokenizer = load(model_name)

print("Model loaded")

prompt = """En quelques phrases, crée un cadre concise pour une fiction interactive qui se déroule dans un contexte médiéval réaliste (9e siècle). La description du setting de départ doit donner quelques indices au joueur d'actions qui lui serait possible de faire (sans pour autant lui indiquer explicitement la voie). Ne produis que la description du contexte à destination du joueur"""

# Generate a response from the model
response = generate(model,
                    tokenizer,
                    prompt=prompt,
                    max_tokens=256,
                    repetition_penalty=2.5,
                    top_p=0.8,
                    temp=0.7)

# Output the response
print(response)