import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pqc_converter import convert_code_to_pqc


def test_convert_rsa():
    sample = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_code", "insecure.py"))
    with open(sample, "r") as f:
        src = f.read()

    converted = convert_code_to_pqc(src)
    print(converted)
    assert "oqs.KeyEncapsulation" in converted


if __name__ == "__main__":
    test_convert_rsa()
