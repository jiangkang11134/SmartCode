"""视图模块 — 引用了 auth.authenticate。"""
from __future__ import annotations

from auth import authenticate


def login_view(username: str, password: str) -> dict:
    """登录视图。"""
    if authenticate(username, password):
        return {"status": "ok", "username": username}
    return {"status": "error", "message": "认证失败"}


def admin_dashboard():
    """管理后台视图。"""
    return {"page": "admin_dashboard", "access": "restricted"}
