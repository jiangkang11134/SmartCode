# @severity: critical
# @rule_id: hardcoded-secret
# @expected_line: 4
# @description: 密钥硬编码（secret = "xxx" 格式）

def decrypt(data):
    secret = "sk-proj-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    from cryptography.fernet import Fernet
    f = Fernet(secret.encode())
    return f.decrypt(data)
