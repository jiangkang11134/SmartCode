# @severity: critical
# @rule_id: hardcoded-secret
# @expected_line: 2
# @description: 密钥在类级别的常量中

class APIClient:
    API_SECRET = "sk-live-aaaaaaaaaaaaaaaaaaaaaaaa"

    def __init__(self):
        self.base_url = "https://api.example.com"

    def request(self, endpoint):
        import requests
        headers = {"X-API-Key": self.API_SECRET}
        return requests.get(f"{self.base_url}/{endpoint}", headers=headers)
