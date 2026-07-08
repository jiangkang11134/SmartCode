# @severity: major
# @rule_id: bare-except
# @expected_line: 4
# @description: except Exception（捕获所有异常）

def safe_divide(a, b):
    try:
        return a / b
    except Exception:
        return None
