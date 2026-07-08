"""严格审查触发判断。

判断条件（优先级从高到低）：
  1. 安全文件路径（auth/ security/ payment/ api/ …）
  2. diff 特征（>200 行、跨 >10 文件、public API 变更）
  3. 历史问题率（同文件 90 天内 >60%）
  4. 新人代码（author 不在已知贡献者列表）
"""

from __future__ import annotations

import time
from pathlib import PurePosixPath
from typing import Any

# 安全文件路径 — 匹配即触发严格
STRICT_PATHS = frozenset({
    "**/auth/**",
    "**/login*",
    "**/security/**",
    "**/encrypt*",
    "**/crypto*",
    "**/payment*",
    "**/billing*",
    "**/api/**",
    "**/middleware*",
    "**/migration*",
    "**/schema*",
    "**/Dockerfile*",
    "**/docker-compose*",
    "**/token*",
    "**/session*",
    "**/oauth*",
})


def _within_days(timestamp: float, days: int) -> bool:
    return time.time() - timestamp < days * 86400


def _is_newcomer(author: str | None, known_authors: set[str] | None = None) -> bool:
    if not author or not known_authors:
        return False
    return author not in known_authors


def should_trigger_strict(
    file_path: str,
    diff_stat: dict[str, Any] | None = None,
    review_store=None,
    author: str | None = None,
    known_authors: set[str] | None = None,
) -> tuple[bool, str]:
    """判断是否应该触发严格审查（启动审查子 Agent）。

    参数:
        file_path: 变更的文件路径
        diff_stat: git diff 统计（changed_lines, touched_files, public_api_changed）
        review_store: ReviewMemoryStore 实例（用于查历史）
        author: git 作者名
        known_authors: 已知贡献者列表

    返回:
        (True, "原因") 或 (False, "")
    """
    # 1. 安全文件路径
    for pattern in STRICT_PATHS:
        if fnmatch.fnmatch(file_path.replace("\\", "/"), pattern):
            return True, f"安全路径: {file_path}"

    # 2. diff 特征
    if diff_stat:
        if diff_stat.get("changed_lines", 0) > 200:
            return True, f"大规模变更 ({diff_stat['changed_lines']} 行)"
        if diff_stat.get("touched_files", 0) > 10:
            return True, f"跨文件变更 ({diff_stat['touched_files']} 个文件)"
        if diff_stat.get("public_api_changed"):
            return True, "public API 签名变更"

    # 3. 历史问题率
    if review_store:
        recent = [
            f for f in review_store.find_by_file(file_path)
            if _within_days(getattr(f, "created_at", 0), 90)
        ]
        if len(recent) >= 3:
            open_count = sum(
                1 for f in recent if getattr(f, "status", "") in ("open", "acknowledged")
            )
            rate = open_count / len(recent)
            if rate >= 0.6:
                return True, f"历史问题率 {rate:.0%}（{open_count}/{len(recent)}）"

    # 4. 新人代码
    if author and _is_newcomer(author, known_authors):
        return True, f"新人代码: {author}"

    return False, ""
