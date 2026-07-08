# @severity: critical
# @rule_id: hardcoded-secret
# @expected_line: 3
# @description: API 密钥硬编码

import requests

API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"

def call_api(endpoint):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get(f"https://api.example.com/{endpoint}", headers=headers)
