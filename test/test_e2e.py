import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from validation import run_full_pipeline


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.sample_dir = os.path.join(os.path.dirname(__file__), "..", "..", "sample_code")

    @patch('validation.analyze_code')
    def test_pipeline_with_online_llm(self, mock_analyze):
        mock_analyze.return_value = "```python\nfrom pqcrypto.kem import kyber512\nkey = kyber512.keypair()\nprint('Generated PQC key')\n```"
        
        report = run_full_pipeline(self.sample_dir, llm_enabled=True, use_local=False)
        
        self.assertIn("files", report)
        file_report = report["files"][0]
        self.assertEqual(file_report["path"], os.path.join(self.sample_dir, "insecure.py"))
        self.assertTrue(len(file_report["issues"]) > 0)
        self.assertIsNotNone(file_report["converted"])
        self.assertIsNotNone(file_report["validation"])
        self.assertTrue(file_report["validation"]["syntax_valid"])

    @patch('validation.local_analyze')
    def test_pipeline_with_local_llm(self, mock_local):
        mock_local.return_value = "```python\nimport oqs\nkem = oqs.KeyEncapsulation('Kyber512')\npublic_key, secret_key = kem.generate_keypair()\nprint('PQC key generated')\n```"
        
        report = run_full_pipeline(self.sample_dir, llm_enabled=True, use_local=True)
        
        file_report = report["files"][0]
        self.assertIsNotNone(file_report["converted"])
        self.assertIsNotNone(file_report["validation"])
        self.assertTrue(file_report["validation"]["syntax_valid"])

    def test_pipeline_without_llm(self):
        report = run_full_pipeline(self.sample_dir)
        
        file_report = report["files"][0]
        self.assertIsNotNone(file_report["converted"])
        self.assertIsNotNone(file_report["validation"])
        self.assertTrue(file_report["validation"]["syntax_valid"])


if __name__ == "__main__":
    unittest.main()