import re

def extract_code(llm_output):
    """
    Extracts code safely from LLM output.
    Handles multiple formats.
    """

    if not llm_output:
        return " No output from LLM"

    #  Case 1: ```python ... ```
    match = re.findall(r"```python(.*?)```", llm_output, re.DOTALL)
    if match:
        return match[0].strip()

    #  Case 2: ``` ... ```
    match = re.findall(r"```(.*?)```", llm_output, re.DOTALL)
    if match:
        return match[0].strip()

    #  Case 3: No code block → try heuristic extraction
    lines = llm_output.split("\n")

    code_lines = []
    for line in lines:
        # crude detection of code-like lines
        if any(keyword in line for keyword in ["import", "from", "def", "class", "=", "(", ")"]):
            code_lines.append(line)

    if code_lines:
        return "\n".join(code_lines)

    #  Fallback
    return " Could not extract code properly. Raw output:\n" + llm_output