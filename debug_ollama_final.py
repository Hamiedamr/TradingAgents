
try:
    import ollama
    print("Ollama library imported successfully.")
except ImportError:
    print("Error: Ollama library not found.")
    exit(1)

client = ollama.Client(host="http://127.0.0.1:11434")

try:
    print("Checking available models...")
    models = client.list()
    model_names = [m['model'] if isinstance(m, dict) else m.model for m in models.models]
    print(f"Available models: {model_names}")
    
    print("Attempting to generate a test embedding...")
    # Explicitly use the clean model name, no fallback magic in debug script
    if "nomic-embed-text" not in model_names and "nomic-embed-text:latest" not in model_names:
         # Optional: auto-pull for convenience in debug script only
         print("Pulling model nomic-embed-text...")
         client.pull("nomic-embed-text")

    response = client.embeddings(
        model="nomic-embed-text",
        prompt="The quick brown fox jumps over the lazy dog."
    )
    
    # Check response format as per clean implementation
    emb = response.embedding if hasattr(response, 'embedding') else response['embedding']
    
    print("Success! Embedding generated.")
    print(f"Vector size: {len(emb)}")
except Exception as e:
    print(f"FAILED: {e}")
