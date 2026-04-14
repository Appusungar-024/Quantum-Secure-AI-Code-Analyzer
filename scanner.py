import subprocess
import json


def run_semgrep_scan(target_path):
    """
    Run a Semgrep scan on *target_path*.
    Returns a list of finding dicts, or an empty list if Semgrep is
    unavailable, produces no output, or returns non-JSON content.
    """
    try:
        result = subprocess.run(
            ["semgrep", "--config=rules/crypto_rules.yaml", target_path, "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if not result.stdout.strip():
            return []
        findings = json.loads(result.stdout)
        return findings.get("results", [])
    except FileNotFoundError:
        # semgrep is not installed — silently skip
        return []
    except (json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        print(f"[scanner] Semgrep scan warning: {e}")
        return []