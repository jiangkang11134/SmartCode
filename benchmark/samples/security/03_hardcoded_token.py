# @severity: critical
# @rule_id: hardcoded-secret
# @expected_line: 2
# @description: Token 硬编码

AUTH_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

def authenticate(user_id):
    if user_id == "admin":
        return {"token": AUTH_TOKEN, "role": "admin"}
    return {"token": "", "role": "user"}
