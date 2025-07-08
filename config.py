CONFIG = {
    "llm_config": {
        "model": "phi3:latest",  # ✅ Matches Ollama's model name
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama-local",
        "api_type": "openai",
        "temperature": 0.3,
        "max_tokens": 300,
        "price": [0.0, 0.0]  # Optional: suppress cost warnings
    }
}