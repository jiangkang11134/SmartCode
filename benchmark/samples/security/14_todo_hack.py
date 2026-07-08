# @severity: minor
# @rule_id: todo-left
# @expected_line: 5
# @description: TODO 和 HACK 注释（行内）

def cache_result(key, value):
    if key and value:
        _cache[key] = value  # HACK: 临时用内存字典
        return True  # TODO: 添加 Redis 支持
    return False

_cache = {}
