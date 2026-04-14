import os
import json
from datetime import datetime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEVERITY_TO_RISK = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}

_RULE_EXPLANATIONS = {
    "RSA_USAGE":      "RSA is vulnerable to quantum attacks (Shor's algorithm). Replaced with Kyber512 KEM via liboqs.",
    "ECDSA_USAGE":    "ECDSA is vulnerable to quantum attacks. Replaced with Dilithium2 digital signature via liboqs.",
    "AES_ECB_USAGE":  "AES-ECB leaks patterns in ciphertext. Replaced with AES-GCM for authenticated encryption.",
    "MD5_USAGE":      "MD5 is cryptographically broken. Replaced with SHA-256.",
    "SHA1_USAGE":     "SHA-1 is deprecated and weak. Replaced with SHA-256.",
}


def _risk_label(severity: str) -> str:
    return _SEVERITY_TO_RISK.get(severity.upper(), "UNKNOWN")


def _collect_issues(report_obj):
    """Flatten all issues from all files into a single list."""
    all_issues = []
    for file_item in report_obj.get("files", []):
        for issue in file_item.get("issues", []):
            all_issues.append({
                "file":     file_item["path"],
                "rule_id":  issue.get("rule_id", "UNKNOWN"),
                "message":  issue.get("message", ""),
                "severity": issue.get("severity", "INFO"),
                "risk":     issue.get("risk") or _risk_label(issue.get("severity", "INFO")),
                "lineno":   issue.get("lineno"),
            })
    return all_issues


# ---------------------------------------------------------------------------
# 8-step structured report
# ---------------------------------------------------------------------------

def generate_structured_output(report_obj):
    """
    Generate the structured output as per the 8-step format.
    """
    output = ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output += f"Quantum-Secure AI Code Analyzer — Report generated at {timestamp}\n"
    output += "=" * 70 + "\n\n"

    all_issues = _collect_issues(report_obj)

    # ------------------------------------------------------------------
    # 1. 🔍 Detected Issues
    # ------------------------------------------------------------------
    output += "1. 🔍 Detected Issues\n"
    if all_issues:
        for issue in all_issues:
            lineno = issue["lineno"] if issue["lineno"] is not None else "?"
            output += (
                f"  - [{issue['severity']}] {issue['file']}:{lineno} "
                f"— {issue['rule_id']}: {issue['message']}\n"
            )
    else:
        output += "  ✅ No cryptographic issues detected.\n"
    output += "\n"

    # ------------------------------------------------------------------
    # 2. ⚠️ Risk Analysis
    # ------------------------------------------------------------------
    output += "2. ⚠️ Risk Analysis\n"
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for issue in all_issues:
        risk = issue["risk"]
        if risk not in risk_counts:
            risk_counts[risk] = 0
        risk_counts[risk] += 1
        explanation = _RULE_EXPLANATIONS.get(issue["rule_id"], issue["message"])
        output += f"  - {risk}: {issue['rule_id']} → {explanation}\n"
    known = risk_counts["HIGH"] + risk_counts["MEDIUM"] + risk_counts["LOW"]
    output += (
        f"  Summary: HIGH: {risk_counts['HIGH']}, "
        f"MEDIUM: {risk_counts['MEDIUM']}, LOW: {risk_counts['LOW']}"
    )
    if risk_counts.get("UNKNOWN"):
        output += f", UNKNOWN: {risk_counts['UNKNOWN']}"
    output += "\n\n"

    # ------------------------------------------------------------------
    # 3. 🔄 Recommended Fixes
    # ------------------------------------------------------------------
    output += "3. 🔄 Recommended Fixes\n"
    files_with_issues = [f for f in report_obj.get("files", []) if f.get("issues")]
    if files_with_issues:
        for file_item in files_with_issues:
            output += f"  - {file_item['path']}: Apply quantum-safe transformations (see converted code below).\n"
    else:
        output += "  No fixes required.\n"
    output += "\n"

    # ------------------------------------------------------------------
    # 4. ✅ Quantum-Safe Converted Code
    # ------------------------------------------------------------------
    output += "4. ✅ Quantum-Safe Converted Code\n"
    any_converted = False
    for file_item in report_obj.get("files", []):
        if file_item.get("converted"):
            any_converted = True
            output += f"  File: {file_item['path']}\n"
            output += "  ```python\n"
            for line in file_item["converted"].splitlines():
                output += f"  {line}\n"
            output += "  ```\n\n"
    if not any_converted:
        output += "  No conversions were performed.\n\n"

    # ------------------------------------------------------------------
    # 5. 📘 Explanation of Changes
    # ------------------------------------------------------------------
    output += "5. 📘 Explanation of Changes\n"
    applied_rules = {issue["rule_id"] for issue in all_issues}
    if applied_rules:
        for rule_id in sorted(applied_rules):
            explanation = _RULE_EXPLANATIONS.get(rule_id, f"{rule_id}: Replaced with quantum-safe alternative.")
            output += f"  - {explanation}\n"
        if applied_rules & {"RSA_USAGE", "ECDSA_USAGE"}:
            output += "  - Added `import oqs` where necessary.\n"
    else:
        output += "  No changes were required.\n"
    output += "\n"

    # ------------------------------------------------------------------
    # 6. 🧪 Validation Results
    # ------------------------------------------------------------------
    output += "6. 🧪 Validation Results\n"
    for file_item in report_obj.get("files", []):
        val = file_item.get("validation")
        if val:
            syntax_status = "✅ Valid" if val.get("syntax_valid") else "❌ Invalid"
            remaining = val.get("remaining_issues", [])
            output += f"  - {file_item['path']}: Syntax {syntax_status}"
            if val.get("error"):
                output += f" (Error: {val['error']})"
            if remaining:
                output += f", {len(remaining)} remaining issue(s) after conversion"
            output += "\n"
    if not any(f.get("validation") for f in report_obj.get("files", [])):
        output += "  No validation data available.\n"
    output += "\n"

    # ------------------------------------------------------------------
    # 7. 🤖 LLM Analysis (if available)
    # ------------------------------------------------------------------
    output += "7. 🤖 LLM Analysis\n"
    any_llm = False
    for file_item in report_obj.get("files", []):
        if file_item.get("llm_output"):
            any_llm = True
            output += f"  File: {file_item['path']}\n"
            output += f"  {file_item['llm_output']}\n"
            if file_item.get("llm_fix"):
                output += "  LLM-suggested fix:\n"
                output += "  ```python\n"
                for line in file_item["llm_fix"].splitlines():
                    output += f"  {line}\n"
                output += "  ```\n"
            output += "\n"
    if not any_llm:
        output += "  LLM analysis was not enabled or produced no output.\n\n"

    # ------------------------------------------------------------------
    # 8. 📊 Semgrep Findings
    # ------------------------------------------------------------------
    output += "8. 📊 Semgrep Findings\n"
    semgrep = report_obj.get("semgrep", [])
    if semgrep:
        for finding in semgrep:
            check_id = finding.get("check_id", "unknown")
            path = finding.get("path", "unknown")
            start = finding.get("start", {}).get("line", "?")
            msg = finding.get("extra", {}).get("message", "")
            output += f"  - [{check_id}] {path}:{start} — {msg}\n"
    else:
        output += "  No Semgrep findings (Semgrep may not be installed or no rules matched).\n"
    output += "\n"

    return output


# ---------------------------------------------------------------------------
# File output helpers
# ---------------------------------------------------------------------------

def write_reports(report_obj, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(out_dir, exist_ok=True)

    # JSON report
    json_path = os.path.join(out_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_obj, f, indent=2)

    # HTML report
    structured_text = generate_structured_output(report_obj)
    html_path = os.path.join(out_dir, "report.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
        f.write("  <meta charset='UTF-8'>\n")
        f.write("  <title>Quantum-Secure AI Code Analyzer — Report</title>\n")
        f.write("  <style>\n")
        f.write("    body { font-family: monospace; background:#1e1e2e; color:#cdd6f4; padding:2rem; }\n")
        f.write("    h1 { color:#cba6f7; } h2 { color:#89b4fa; }\n")
        f.write("    pre { background:#181825; padding:1rem; border-radius:8px; white-space:pre-wrap; }\n")
        f.write("    li { margin-bottom:.4rem; }\n")
        f.write("  </style>\n</head>\n<body>\n")
        f.write("<h1>Quantum-Secure AI Code Analyzer</h1>\n")
        f.write("<h2>File Summary</h2>\n<ul>\n")
        for item in report_obj.get("files", []):
            count = len(item.get("issues", []))
            label = "issues" if count != 1 else "issue"
            f.write(f"  <li>{item['path']}: {count} {label}</li>\n")
        f.write("</ul>\n")
        f.write("<h2>Structured Output</h2>\n<pre>\n")
        f.write(structured_text.replace("<", "&lt;").replace(">", "&gt;"))
        f.write("</pre>\n</body>\n</html>\n")

    return {"json": json_path, "html": html_path}
