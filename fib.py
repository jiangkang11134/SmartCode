"""斐波那契数列 — 优化版。

提供三种实现，按性能从高到低排列：
1. fibonacci_fast(n)  — 迭代式快速倍增法 O(log n)，无递归栈开销
2. fibonacci_matrix(n) — 矩阵快速幂法 O(log n)，教学友好
3. fibonacci_iter(n)  — 迭代法 O(n)，适合小 n
"""

from __future__ import annotations

import functools
from typing import Tuple


# ============================================================
# 实现 1：迭代式快速倍增法（推荐，性能最优）
# ============================================================

def fibonacci_fast(n: int) -> int:
    """返回第 n 个斐波那契数（迭代式快速倍增法，O(log n)）。

    使用快速倍增恒等式：
        F(2k)   = F(k) * (2*F(k+1) - F(k))
        F(2k+1) = F(k+1)^2 + F(k)^2

    迭代实现避免递归，无栈溢出风险，适合大 n。

    Args:
        n: 非负整数索引（n >= 0）。

    Returns:
        第 n 个斐波那契数。

    Raises:
        TypeError: 如果 n 不是整数。
        ValueError: 如果 n 为负数。

    Examples:
        >>> fibonacci_fast(0)
        0
        >>> fibonacci_fast(1)
        1
        >>> fibonacci_fast(10)
        55
        >>> fibonacci_fast(100)
        354224848179261915075
    """
    if not isinstance(n, int):
        raise TypeError("n 必须是整数")
    if n < 0:
        raise ValueError("n 不能为负数")

    if n <= 1:
        return n

    # 迭代式快速倍增：从最高位向最低位处理
    # 找到 n 的最高位
    bits = n.bit_length()
    # a = F(0) = 0, b = F(1) = 1
    a, b = 0, 1

    # 从次高位开始遍历每一位
    for i in range(bits - 1, -1, -1):
        # 先计算 F(2k) 和 F(2k+1)
        # F(2k) = F(k) * (2*F(k+1) - F(k))
        c = a * (2 * b - a)
        # F(2k+1) = F(k+1)^2 + F(k)^2
        d = a * a + b * b

        if (n >> i) & 1:
            # 如果当前位是 1：F(2k+1), F(2k+2)
            # F(2k+1) = d, F(2k+2) = F(2k+1) + F(2k) = d + c
            a, b = d, c + d
        else:
            # 如果当前位是 0：F(2k), F(2k+1)
            a, b = c, d

    return a


# ============================================================
# 实现 2：矩阵快速幂法（教学友好）
# ============================================================

def _mat_mul(a: Tuple[int, int, int, int],
             b: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    """2x2 矩阵乘法。"""
    return (
        a[0] * b[0] + a[1] * b[2],
        a[0] * b[1] + a[1] * b[3],
        a[2] * b[0] + a[3] * b[2],
        a[2] * b[1] + a[3] * b[3],
    )


def _mat_pow(mat: Tuple[int, int, int, int], n: int) -> Tuple[int, int, int, int]:
    """矩阵快速幂（二进制分解）。"""
    result = (1, 0, 0, 1)  # 单位矩阵
    base = mat
    while n:
        if n & 1:
            result = _mat_mul(result, base)
        base = _mat_mul(base, base)
        n >>= 1
    return result


def fibonacci_matrix(n: int) -> int:
    """返回第 n 个斐波那契数（矩阵快速幂法，O(log n)）。

    利用恒等式：
        [F(n+1) F(n)  ]   = [1 1]^n
        [F(n)   F(n-1)]     [1 0]

    Args:
        n: 非负整数索引。

    Returns:
        第 n 个斐波那契数。

    Raises:
        TypeError: 如果 n 不是整数。
        ValueError: 如果 n 为负数。
    """
    if not isinstance(n, int):
        raise TypeError("n 必须是整数")
    if n < 0:
        raise ValueError("n 不能为负数")
    if n <= 1:
        return n

    # 基础矩阵 [[1,1],[1,0]]
    base = (1, 1, 1, 0)
    result = _mat_pow(base, n)
    return result[1]  # F(n)


# ============================================================
# 实现 3：记忆化递归（带缓存，适合重复调用场景）
# ============================================================

@functools.lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    """返回第 n 个斐波那契数（记忆化递归，O(n) 首次调用）。

    使用 @lru_cache 自动缓存结果。
    适合多次调用不同 n 的场景。

    Args:
        n: 非负整数索引。

    Returns:
        第 n 个斐波那契数。

    Raises:
        TypeError: 如果 n 不是整数。
        ValueError: 如果 n 为负数。
    """
    if not isinstance(n, int):
        raise TypeError("n 必须是整数")
    if n < 0:
        raise ValueError("n 不能为负数")
    if n <= 1:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


# ============================================================
# 统一接口（默认使用最优实现）
# ============================================================

def fibonacci(n: int) -> int:
    """返回第 n 个斐波那契数（默认使用迭代式快速倍增法，O(log n)）。

    这是推荐使用的统一入口函数，内部自动选择最优实现。

    Args:
        n: 非负整数索引。

    Returns:
        第 n 个斐波那契数。

    Raises:
        TypeError: 如果 n 不是整数。
        ValueError: 如果 n 为负数。

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(10)
        55
        >>> fibonacci(50)
        12586269025
        >>> fibonacci(100)
        354224848179261915075
    """
    return fibonacci_fast(n)


# 清除缓存，方便测试
def clear_cache() -> None:
    """清除 fibonacci_cached 的缓存。"""
    fibonacci_cached.cache_clear()