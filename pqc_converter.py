import ast


class PQCTransformer(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        func = node.func
        # Get attribute chain
        parts = []
        cur = func
        while isinstance(cur, ast.Attribute):
            parts.insert(0, cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.insert(0, cur.id)

        # RSA.generate -> oqs.KeyEncapsulation('Kyber512').generate_keypair()
        if parts == ["RSA", "generate"]:
            # Create oqs.KeyEncapsulation('Kyber512').generate_keypair()
            oqs_attr = ast.Attribute(value=ast.Name(id='oqs', ctx=ast.Load()), attr='KeyEncapsulation', ctx=ast.Load())
            kem_call = ast.Call(func=oqs_attr, args=[ast.Constant(value='Kyber512')], keywords=[])
            gen_attr = ast.Attribute(value=kem_call, attr='generate_keypair', ctx=ast.Load())
            new = ast.Call(func=gen_attr, args=[], keywords=[])
            return ast.copy_location(new, node)

        # ecdsa.generate_key -> oqs.Signature('Dilithium2').generate_keypair()
        if parts == ["ecdsa", "generate_key"]:
            sig_attr = ast.Attribute(value=ast.Name(id='oqs', ctx=ast.Load()), attr='Signature', ctx=ast.Load())
            sig_call = ast.Call(func=sig_attr, args=[ast.Constant(value='Dilithium2')], keywords=[])
            gen_attr = ast.Attribute(value=sig_call, attr='generate_keypair', ctx=ast.Load())
            new = ast.Call(func=gen_attr, args=[], keywords=[])
            return ast.copy_location(new, node)

        # AES.new(..., AES.MODE_ECB) -> AES.new(..., AES.MODE_GCM)
        if parts == ["AES", "new"] and len(node.args) >= 2:
            # Check if second arg is AES.MODE_ECB
            if isinstance(node.args[1], ast.Attribute):
                ecb_parts = []
                ecb_cur = node.args[1]
                while isinstance(ecb_cur, ast.Attribute):
                    ecb_parts.insert(0, ecb_cur.attr)
                    ecb_cur = ecb_cur.value
                if isinstance(ecb_cur, ast.Name):
                    ecb_parts.insert(0, ecb_cur.id)
                if ecb_parts == ["AES", "MODE_ECB"]:
                    # Replace with AES.MODE_GCM
                    gcm_attr = ast.Attribute(value=ast.Name(id='AES', ctx=ast.Load()), attr='MODE_GCM', ctx=ast.Load())
                    node.args[1] = gcm_attr
                    return node

        # hashlib.md5 -> hashlib.sha256
        if parts == ["hashlib", "md5"]:
            sha_attr = ast.Attribute(value=ast.Name(id='hashlib', ctx=ast.Load()), attr='sha256', ctx=ast.Load())
            new = ast.Call(func=sha_attr, args=node.args, keywords=node.keywords)
            return ast.copy_location(new, node)

        # hashlib.sha1 -> hashlib.sha256
        if parts == ["hashlib", "sha1"]:
            sha_attr = ast.Attribute(value=ast.Name(id='hashlib', ctx=ast.Load()), attr='sha256', ctx=ast.Load())
            new = ast.Call(func=sha_attr, args=node.args, keywords=node.keywords)
            return ast.copy_location(new, node)

        return node


def convert_code_to_pqc(code_str):
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        return code_str

    transformer = PQCTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    try:
        new_code = ast.unparse(new_tree)
    except AttributeError:
        # For older Python versions, fall back to returning original code
        return code_str

    # Add import oqs if oqs is used
    if "oqs." in new_code and "import oqs" not in new_code:
        new_code = "import oqs\n" + new_code

    return new_code
