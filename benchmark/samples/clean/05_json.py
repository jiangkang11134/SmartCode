# @description: 干净代码，无安全问题
# @expected_issues: 0

"""JSON 处理 — 使用安全的 json 库。"""
from __future__ import annotations

import json


def parse_json(data: str) -> dict | None:
    """安全解析 JSON 字符串。"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def to_json(obj: dict) -> str:
    """将对象转为 JSON 字符串。"""
    return json.dumps(obj, ensure_ascii=False, indent=2)
