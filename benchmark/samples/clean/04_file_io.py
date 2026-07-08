# @description: 干净代码，无安全问题
# @expected_issues: 0

"""文件读取工具 — 使用安全的 with 语句。"""
from __future__ import annotations

from pathlib import Path


def read_file_safe(path: str) -> str | None:
    """安全读取文件内容。"""
    p = Path(path)
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def write_file_safe(path: str, content: str) -> bool:
    """安全写入文件。"""
    try:
        Path(path).write_text(content, encoding="utf-8")
        return True
    except OSError:
        return False
