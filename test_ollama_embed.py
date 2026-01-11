
import litellm
import os

# Mock Config similar to default_config.py
config = {
    "backend_url": "http://localhost:11434/v1" 
}

# Logic from memory.py
base_url = config.get("backend_url")
if base_url:
    base_url = base_url.replace("/v1", "").replace("localhost", "127.0.0.1")

print(f"Testing with api_base: {base_url}")

try:
    response = litellm.embedding(
        model="ollama/nomic-embed-text", 
        input=["Hello world"],
        api_base=base_url
    )
    print("Success! Embedding generated.")
    print("Vector length:", len(response['data'][0]['embedding']))
except Exception as e:
    print(f"Error: {e}")
