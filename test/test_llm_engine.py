import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if os.getenv("OPENAI_API_KEY") is None:
    print("OPENAI_API_KEY not set, skipping llm_engine execution.")
    sys.exit(0)

from llm_engine import analyze_code

def test_analyze_code():
    code = open("../sample_code/insecure.py").read()
    result = analyze_code(code)
    print(result)
    assert result is not None

if __name__ == "__main__":
    test_analyze_code()