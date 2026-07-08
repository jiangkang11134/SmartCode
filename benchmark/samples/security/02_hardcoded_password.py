# @severity: critical
# @rule_id: hardcoded-secret
# @expected_line: 4
# @description: 数据库密码硬编码

import mysql.connector

DB_PASSWORD = "pass123456"

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="admin",
        password=DB_PASSWORD,
        database="production"
    )
