# @description: 白名单前缀 test_，应跳过审查
# @expected_skip: true

"""测试配置文件 — 行起始于 test_ 前缀的跳过审查。"""

test_db_url = "postgresql://test:test123@localhost:5432/testdb"
test_api_key = "sk-test-key-not-real"
