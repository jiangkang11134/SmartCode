"""认证模块 — 定义 authenticate 函数供其他模块引用。"""
from __future__ import annotations

import hashlib


def authenticate(username: str, password: str) -> bool:
    """验证用户身份。"""
    stored_hash = _get_stored_hash(username)
    if not stored_hash:
        return False
    return hashlib.sha256(password.encode()).hexdigest() == stored_hash


def _get_stored_hash(username: str) -> str | None:
    """模拟从数据库获取密码哈希。"""
    users = {"admin": "hash1", "user": "hash2"}
    return users.get(username)
