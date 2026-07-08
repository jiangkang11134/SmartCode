# @description: 干净代码，无安全问题
# @expected_issues: 0

"""斐波那契数列计算。"""
from __future__ import annotations


def fibonacci(n: int) -> int:
    """计算第 n 个斐波那契数。"""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
