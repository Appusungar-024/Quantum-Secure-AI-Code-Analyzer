import requests
import json

def local_analyze(code):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "codellama",
            "prompt": f"Analyze this code for quantum-vulnerable cryptography. Explain issue briefly and provide ONLY fixed code inside ```python block.\n\nCode:\n{code}",
            "stream": False  # Disable streaming for simplicity
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.status_code} {response.text}")
    
    data = response.json()
    return data.get("response", "")