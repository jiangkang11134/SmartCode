# @description: 干净代码，无安全问题
# @expected_issues: 0

"""Date utility functions."""
from __future__ import annotations

from datetime import datetime, timedelta


def format_date(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def days_between(d1: datetime, d2: datetime) -> int:
    """计算两个日期之间的天数。"""
    return abs((d2 - d1).days)
