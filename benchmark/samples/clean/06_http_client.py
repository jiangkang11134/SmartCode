# @description: 干净代码，无安全问题
# @expected_issues: 0

"""HTTP 客户端 — 使用 requests 库。"""
from __future__ import annotations

import os


def fetch_data(api_url: str) -> dict | None:
    """获取 API 数据（从环境变量读密钥）。"""
    import requests

    token = os.environ.get("API_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None
