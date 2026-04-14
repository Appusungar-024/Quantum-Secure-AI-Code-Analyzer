# Quantum-Secure AI Code Analyzer

An automated system that analyzes Python source code and converts vulnerable cryptographic implementations into quantum-safe alternatives.

## Features

- **Code Analysis**: Detects quantum-vulnerable cryptography (RSA, ECC, AES-ECB, MD5, SHA1)
- **Risk Assessment**: Assigns HIGH/MEDIUM/LOW risk levels to vulnerabilities
- **Quantum-Safe Conversion**: Automatically transforms code to use post-quantum cryptography (Kyber, Dilithium, SHA-256, AES-GCM)
- **Validation**: Ensures converted code is syntactically valid and secure
- **Web Interface**: Responsive frontend for easy code analysis
- **API Endpoints**: RESTful API for integration
- **LLM Integration**: Optional AI-assisted fixes (requires API key)

## Installation

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `cd quantum-secure-ai/backend && uvicorn main:app --host 0.0.0.0 --port 8000`

## Usage

### Web Interface
- Open http://localhost:8000
- Enter Python code or upload a file
- Click "Analyze Code"
- View results with detected issues, risk analysis, fixes, and converted code

### API Usage
```bash
# Analyze a file
curl -X GET "http://localhost:8000/analyze/?path=sample_code"

# Convert code
curl -X POST "http://localhost:8000/convert/" -H "Content-Type: application/json" -d '{"path": "sample_code/insecure.py"}'
```

## Architecture

- **Backend**: FastAPI with Python AST parsing and liboqs for PQC
- **Frontend**: HTML/CSS/JavaScript with Bootstrap for responsiveness
- **Detection**: Rule-based patterns for crypto vulnerabilities
- **Conversion**: AST transformation to quantum-safe implementations
- **Validation**: Syntax checking and re-scanning for remaining issues

## Supported Conversions

- RSA.generate() → oqs.KeyEncapsulation('Kyber512').generate_keypair()
- ecdsa.generate_key() → oqs.Signature('Dilithium2').generate_keypair()
- AES.MODE_ECB → AES.MODE_GCM
- hashlib.md5() → hashlib.sha256()
- hashlib.sha1() → hashlib.sha256()

## Requirements

- Python 3.9+
- liboqs-python for post-quantum cryptography
- FastAPI for web framework
- Bootstrap for responsive UI

## Security Note

This tool helps migrate to quantum-safe cryptography but should be used as part of a comprehensive security strategy. Always test converted code thoroughly.

      - name: Install dependencies
        run: pip install semgrep

      - name: Run scanner
        run: semgrep --config backend/rules/crypto_rules.yaml .
