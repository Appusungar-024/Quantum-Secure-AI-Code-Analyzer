from dotenv import load_dotenv
import os

openai_available = False
OpenAI = None
client = None

def analyze_code(code_snippet):
    if not openai_available or client is None:
        return "OpenAI not available"

    prompt = f"""
    Analyze this code for quantum-vulnerable cryptography.

    STRICT INSTRUCTIONS:
    1. Explain issue briefly
    2. Provide ONLY fixed code inside ```python block

    Code:
    {code_snippet}
    """

    response = client.chat.completions.create(
        model="gpt-5.3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content