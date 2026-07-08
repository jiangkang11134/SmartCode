# @severity: major
# @rule_id: bare-except
# @expected_line: 5
# @description: 裸 except 捕获所有异常

def read_config(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        # 捕获了所有异常，隐藏了具体错误
        return ""
