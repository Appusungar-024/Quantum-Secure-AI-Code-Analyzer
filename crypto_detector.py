import ast
import os
import yaml


def load_rules():
    rules_path = os.path.join(os.path.dirname(__file__), "rules", "crypto_rules.yaml")
    with open(rules_path, "r") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])


def _get_attr_chain(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.insert(0, node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.insert(0, node.id)
    return parts


def _call_matches_pattern(call_node, pattern):
    # Normalize pattern like "RSA.generate(...)" -> "RSA.generate"
    p = pattern.split("(", 1)[0].strip()
    p = p.replace("...", "")
    p = p.strip()
    parts = [part for part in p.split(".") if part]

    func = call_node.func
    # Attribute chain: RSA.generate -> ["RSA","generate"]
    if isinstance(func, ast.Attribute):
        chain = _get_attr_chain(func)
        return chain == parts

    # Simple name: sha1()
    if isinstance(func, ast.Name):
        return [func.id] == parts

    return False


def detect_in_code(code_str):
    rules = load_rules()
    results = []
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        return results

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for rule in rules:
                pattern = rule.get("pattern")
                if not pattern:
                    continue
                if _call_matches_pattern(node, pattern):
                    results.append({
                        "rule_id": rule.get("id"),
                        "message": rule.get("message"),
                        "severity": rule.get("severity"),
                        "risk": rule.get("risk"),
                        "lineno": getattr(node, "lineno", None),
                        "col_offset": getattr(node, "col_offset", None),
                    })
    return results


def detect_file(path):
    with open(path, "r") as f:
        code = f.read()
    return detect_in_code(code)
