import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scanner import run_semgrep_scan

issues = run_semgrep_scan("../sample_code")
print(issues)