import os
import ast
from scanner import run_semgrep_scan
from crypto_detector import detect_file, detect_in_code
from pqc_converter import convert_code_to_pqc
from converter import extract_code
from llm_engine import analyze_code
from local_llm import local_analyze


def validate_converted_code(code_str):
    """
    Validate converted code: check syntax and re-scan for crypto issues.
    Returns dict with 'syntax_valid', 'remaining_issues', 'error'
    """
    result = {
        'syntax_valid': False,
        'remaining_issues': [],
        'error': None
    }
    try:
        ast.parse(code_str)
        result['syntax_valid'] = True
        result['remaining_issues'] = detect_in_code(code_str)
    except SyntaxError as e:
        result['error'] = str(e)
    return result


def run_full_pipeline(target_dir, llm_enabled=False, use_local=False):
    results = []
    # 1) Semgrep findings
    semgrep_findings = run_semgrep_scan(target_dir)

    # 2) Walk files and run crypto_detector + converter
    for root, _, files in os.walk(target_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(root, fname)
            issues = detect_file(path)
            converted = None
            llm_output = None
            llm_fix = None
            validation = None

            if issues:
                with open(path, "r") as f:
                    src = f.read()
                converted = convert_code_to_pqc(src)
                validation = validate_converted_code(converted)

                if llm_enabled:
                    try:
                        if use_local:
                            llm_output = local_analyze(src)
                        else:
                            llm_output = analyze_code(src)
                        llm_fix = extract_code(llm_output)
                    except Exception as e:
                        llm_output = f"LLM error: {e}"
                        llm_fix = None

            results.append({
                "path": path,
                "issues": issues,
                "converted": converted,
                "validation": validation,
                "llm_output": llm_output,
                "llm_fix": llm_fix,
            })

    return {
        "semgrep": semgrep_findings,
        "files": results,
    }
