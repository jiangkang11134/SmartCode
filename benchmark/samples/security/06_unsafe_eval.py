# @severity: critical
# @rule_id: unsafe-eval
# @expected_line: 5
# @description: 直接使用 eval 执行用户输入

def calculate(expression):
    result = eval(expression)
    return result

def process_input(user_input):
    # 用户输入直接传入 eval
    return calculate(user_input)
