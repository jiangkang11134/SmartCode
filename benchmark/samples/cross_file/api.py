"""API 模块 — 引用了 auth.authenticate。"""
from __future__ import annotations

from auth import authenticate


def api_login(request: dict) -> dict:
    """API 登录接口。"""
    username = request.get("username", "")
    password = request.get("password", "")
    if authenticate(username, password):
        return {"code": 0, "token": "xxx"}
    return {"code": 401, "message": "认证失败"}
