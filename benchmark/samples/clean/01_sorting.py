# @description: 干净代码，无安全问题
# @expected_issues: 0

"""数组排序工具函数。"""
from __future__ import annotations


def bubble_sort(arr: list[int]) -> list[int]:
    """冒泡排序实现。"""
    result = arr[:]
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result
