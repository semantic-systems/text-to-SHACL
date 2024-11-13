import time

from openai import OpenAI
from utils import get_all_models

# API configuration
api_key = 'cc0637db9153801f5d4b158dbb9f504f'
base_url = "https://chat-ai.academiccloud.de/v1"
available_models = get_all_models(api_key)

model = available_models[-1]
print(f"Model: {model}\n")  # Choose any available model

# Start OpenAI client
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# Read SHACL shapes graph
filepath ="shapes/kinderzuschlag_long.ttl"
with open(filepath, "r") as file:
    shapes_graph = file.read()

# Get response
start_time = time.time()
chat_completion = client.chat.completions.create(
    messages=[{"role": "system", "content": "You are an expert in ontology building."},
              {"role": "user", "content": "Generate an ontology that describes the following SHACL shapes graph. Use turtle serialization to represent the ontology."
                                          f"\n \n SHAPES GRAPH \n {shapes_graph}"}],
    model=model,
    temperature=0.7,
    top_p=0.8
)
print(f"Time taken: {time.time() - start_time:.2f} seconds")

# Print full response as JSON
# You can extract the response text from the JSON object
print(chat_completion.choices[0].message.content)