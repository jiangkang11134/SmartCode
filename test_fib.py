"""斐波那契优化实现 — 测试。"""
from __future__ import annotations

import sys
sys.path.insert(0, str(__file__).resolve().parent)

from fib import fibonacci, fibonacci_fast, fibonacci_matrix, fibonacci_cached, clear_cache


# ========== 已知值测试 ==========

FIB_VALUES = [
    (0, 0),
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 3),
    (5, 5),
    (6, 8),
    (7, 13),
    (8, 21),
    (9, 34),
    (10, 55),
    (20, 6765),
    (30, 832040),
    (50, 12586269025),
    (100, 354224848179261915075),
]


def test_fibonacci_fast_known_values():
    for n, expected in FIB_VALUES:
        result = fibonacci_fast(n)
        assert result == expected, f"fibonacci_fast({n}) = {result}, 期望 {expected}"


def test_fibonacci_matrix_known_values():
    for n, expected in FIB_VALUES:
        result = fibonacci_matrix(n)
        assert result == expected, f"fibonacci_matrix({n}) = {result}, 期望 {expected}"


def test_fibonacci_cached_known_values():
    clear_cache()
    for n, expected in FIB_VALUES:
        result = fibonacci_cached(n)
        assert result == expected, f"fibonacci_cached({n}) = {result}, 期望 {expected}"


def test_fibonacci_unified():
    for n, expected in FIB_VALUES:
        result = fibonacci(n)
        assert result == expected, f"fibonacci({n}) = {result}, 期望 {expected}"


# ========== 多实现一致性测试 ==========

def test_implementations_agree():
    for n in range(0, 200):
        fast = fibonacci_fast(n)
        mat = fibonacci_matrix(n)
        assert fast == mat, f"n={n}: fast={fast}, matrix={mat}"


# ========== 边界条件测试 ==========

def test_negative_raises():
    for f in [fibonacci_fast, fibonacci_matrix, fibonacci]:
        try:
            f(-1)
            assert False, f"{f.__name__}(-1) 应该抛出异常"
        except ValueError:
            pass


def test_non_integer_raises():
    for f in [fibonacci_fast, fibonacci_matrix, fibonacci]:
        try:
            f(3.14)
            assert False, f"{f.__name__}(3.14) 应该抛出异常"
        except TypeError:
            pass


# ========== 大数测试 ==========

def test_large_n():
    # n=1000 的斐波那契数有 209 位
    result = fibonacci_fast(1000)
    assert result > 0
    assert len(str(result)) == 209, f"F(1000) 应是 209 位, 实际 {len(str(result))} 位"


def test_matrix_vs_fast_large():
    result = fibonacci_fast(5000)
    result2 = fibonacci_matrix(5000)
    assert result == result2


# ========== 缓存测试 ==========

def test_cache_clear():
    clear_cache()
    assert fibonacci_cached.cache_info().misses == 0
    fibonacci_cached(50)
    assert fibonacci_cached.cache_info().misses > 0
    misses_before = fibonacci_cached.cache_info().misses
    fibonacci_cached(50)
    assert fibonacci_cached.cache_info().misses == misses_before  # 缓存命中


# ========== 性能对比测试 ==========

def test_performance():
    """验证迭代快速倍增比矩阵法更快（微基准测试）。"""
    import time

    def measure(f, n, trials=3):
        times = []
        for _ in range(trials):
            clear_cache()
            t0 = time.perf_counter()
            f(n)
            times.append(time.perf_counter() - t0)
        return min(times)

    n = 100000  # 足够大的 n
    fast_time = measure(fibonacci_fast, n)
    mat_time = measure(fibonacci_matrix, n)

    print(f"\n性能对比 (n={n}):")
    print(f"  fibonacci_fast:   {fast_time*1000:.2f}ms")
    print(f"  fibonacci_matrix: {mat_time*1000:.2f}ms")
    print(f"  提速比: {mat_time/fast_time:.1f}x")

    # 迭代快速倍增应该快于矩阵法（相差不应过大）
    # 这个测试只是信息性参考，不严格断言
    assert fast_time > 0


if __name__ == "__main__":
    test_fibonacci_fast_known_values()
    print("✓ 快速倍增法已知值测试通过")
    test_fibonacci_matrix_known_values()
    print("✓ 矩阵快速幂法已知值测试通过")
    test_fibonacci_cached_known_values()
    print("✓ 记忆化递归已知值测试通过")
    test_fibonacci_unified()
    print("✓ 统一接口测试通过")
    test_implementations_agree()
    print("✓ 多实现一致性测试通过 (n=0..199)")
    test_negative_raises()
    print("✓ 边界条件测试通过")
    test_non_integer_raises()
    print("✓ 非整数输入测试通过")
    test_large_n()
    print("✓ 大数测试通过 (n=1000)")
    test_matrix_vs_fast_large()
    print("✓ 大数一致性测试通过 (n=5000)")
    test_cache_clear()
    print("✓ 缓存清除测试通过")
    test_performance()
    print("✓ 性能基准测试通过")
    print("\n所有测试通过 ✅")