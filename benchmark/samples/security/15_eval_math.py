# @severity: critical
# @rule_id: unsafe-eval
# @expected_line: 6
# @description: eval 解析 JSON 字符串

def parse_input(raw_data):
    # 应使用 json.loads
    result = eval(raw_data)
    return result

def process_math(expr):
    allowed = ["+", "-", "*", "/", "abs"]
    if any(op in expr for op in allowed):
        return eval(expr)
    return 0
