import subprocess
import json

def run_semgrep_scan(target_path):
    result = subprocess.run(
        ["semgrep", "--config=backend/rules/crypto_rules.yaml", target_path, "--json"],
        capture_output=True,
        text=True
    )
    
    findings = json.loads(result.stdout)
    return findings.get("results", [])