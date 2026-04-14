import os
import json


def generate_structured_output(report_obj):
    """
    Generate the structured output as per the 8-step format.
    """
    output = ""

    # 1. 🔍 Detected Issues
    output += "1. 🔍 Detected Issues\n"
    all_issues = []
    for file_item in report_obj.get("files", []):
        for issue in file_item.get("issues", []):
            all_issues.append({
                "file": file_item["path"],
                "rule_id": issue["rule_id"],
                "message": issue["message"],
                "severity": issue["severity"],
                "lineno": issue.get("lineno"),
            })
    if all_issues:
        for issue in all_issues:
            output += f"  - {issue['file']}:{issue['lineno']} - {issue['rule_id']}: {issue['message']}\n"
    else:
        output += "  No cryptographic issues detected.\n"
    output += "\n"

    # 2. ⚠️ Risk Analysis
    output += "2. ⚠️ Risk Analysis\n"
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for file_item in report_obj.get("files", []):
        for issue in file_item.get("issues", []):
            # Assuming risk is in issue, but from detector, need to add
            # For now, map severity to risk: ERROR->HIGH, WARNING->MEDIUM, INFO->LOW
            risk = {"ERROR": "HIGH", "WARNING": "MEDIUM", "INFO": "LOW"}.get(issue["severity"], "UNKNOWN")
            risk_counts[risk] += 1
            output += f"  - {risk}: {issue['message']} (Explanation: {issue['message']})\n"
    output += f"Summary: HIGH: {risk_counts['HIGH']}, MEDIUM: {risk_counts['MEDIUM']}, LOW: {risk_counts['LOW']}\n\n"

    # 3. 🔄 Recommended Fixes
    output += "3. 🔄 Recommended Fixes\n"
    for file_item in report_obj.get("files", []):
        if file_item.get("issues"):
            output += f"  - {file_item['path']}: Apply quantum-safe transformations.\n"
    output += "\n"

    # 4. ✅ Quantum-Safe Converted Code
    output += "4. ✅ Quantum-Safe Converted Code\n"
    for file_item in report_obj.get("files", []):
        if file_item.get("converted"):
            output += f"  File: {file_item['path']}\n"
            output += "```python\n" + file_item["converted"] + "\n```\n\n"

    # 5. 📘 Explanation of Changes
    output += "5. 📘 Explanation of Changes\n"
    output += "  - RSA.generate() replaced with oqs.KeyEncapsulation('Kyber512').generate_keypair()\n"
    output += "  - ecdsa.generate_key() replaced with oqs.Signature('Dilithium2').generate_keypair()\n"
    output += "  - AES.MODE_ECB replaced with AES.MODE_GCM\n"
    output += "  - hashlib.md5() and hashlib.sha1() replaced with hashlib.sha256()\n"
    output += "  - Added import oqs where necessary.\n"

    return output


def write_reports(report_obj, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "report.json")
    with open(json_path, "w") as f:
        json.dump(report_obj, f, indent=2)

    # Enhanced HTML
    html_path = os.path.join(out_dir, "report.html")
    with open(html_path, "w") as f:
        f.write("<html><body><h1>Analysis Report</h1>\n")
        f.write("<h2>Files</h2>\n<ul>\n")
        for item in report_obj.get("files", []):
            f.write(f"<li>{item['path']}: {len(item.get('issues', []))} issues</li>\n")
        f.write("</ul>\n")
        f.write("<h2>Structured Output</h2>\n<pre>\n")
        f.write(generate_structured_output(report_obj).replace("<", "&lt;").replace(">", "&gt;"))
        f.write("</pre>\n")
        f.write("</body></html>\n")

    return {"json": json_path, "html": html_path}
