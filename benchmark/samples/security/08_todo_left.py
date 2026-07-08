# @severity: minor
# @rule_id: todo-left
# @expected_line: 4
# @description: TODO 注释遗留（行内）

def process_order(order_id):
    result = {"order_id": order_id, "status": "processed"}
    # TODO: 添加验证逻辑
    return result  # FIXME: 处理并发情况
