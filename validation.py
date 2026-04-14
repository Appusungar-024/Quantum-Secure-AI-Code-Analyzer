import os
import ast
import logging
from typing import Dict, Any, List, Optional

from scanner import run_semgrep_scan
from crypto_detector import detect_file, detect_in_code
from pqc_converter import convert_code_to_pqc
from converter import extract_code
from llm_engine import analyze_code
from local_llm import local_analyze

logger = logging.getLogger(__name__)


def validate_converted_code(code_str: Optional[str]) -> Dict[str, Any]:
    """
    Validate converted code: check syntax and re-scan for crypto issues.
    Returns dict with 'syntax_valid', 'remaining_issues', 'error'
    """
    result: Dict[str, Any] = {
        'syntax_valid': False,
        'remaining_issues': [],
        'error': None
    }
    
    if not code_str:
        result['error'] = "No code provided for validation."
        return result

    try:
        ast.parse(code_str)
        result['syntax_valid'] = True
        result['remaining_issues'] = detect_in_code(code_str)
    except SyntaxError as e:
        result['error'] = f"Syntax error: {e}"
    except Exception as e:
        result['error'] = f"Unexpected error during validation: {e}"
        logger.exception("Validation error")
        
    return result


def run_full_pipeline(target_dir: str, llm_enabled: bool = False, use_local: bool = False) -> Dict[str, Any]:
    """
    Run the complete security scanning and conversion pipeline.
    
    Args:
        target_dir: The directory to scan.
        llm_enabled: Whether to use LLM for analysis and fixes.
        use_local: Whether to use local LLM.
        
    Returns:
        Dict containing semgrep findings and file-specific results.
    """
    results: List[Dict[str, Any]] = []
    
    # 1) Semgrep findings
    try:
        semgrep_findings = run_semgrep_scan(target_dir)
    except Exception as e:
        logger.error(f"Semgrep scan failed: {e}")
        semgrep_findings = {"error": str(e)}

    # 2) Walk files and run crypto_detector + converter
    for root, _, files in os.walk(target_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
                
            path = os.path.join(root, fname)
            
            try:
                issues = detect_file(path)
            except Exception as e:
                logger.error(f"Error checking {path} for issues: {e}")
                issues = []
                
            converted = None
            llm_output = None
            llm_fix = None
            validation = None

            if issues:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        src = f.read()
                        
                    converted = convert_code_to_pqc(src)
                    validation = validate_converted_code(converted)

                    if llm_enabled:
                        try:
                            if use_local:
                                llm_output = local_analyze(src)
                            else:
                                llm_output = analyze_code(src)
                            llm_fix = extract_code(llm_output) if llm_output else None
                        except Exception as e:
                            llm_output = f"LLM error: {e}"
                            llm_fix = None
                            logger.error(f"LLM processing failed for {path}: {e}")
                            
                except Exception as e:
                    logger.error(f"Failed to process file {path}: {e}")
                    validation = {"error": f"Processing fail: {e}"}

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
