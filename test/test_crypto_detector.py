import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto_detector import detect_file


def test_detect_rsa():
    sample = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_code", "insecure.py"))
    issues = detect_file(sample)
    print("Issues:", issues)
    assert isinstance(issues, list)
    assert any(i.get("rule_id") == "detect-rsa" for i in issues)


if __name__ == "__main__":
    test_detect_rsa()
