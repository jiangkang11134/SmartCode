# @severity: critical
# @rule_id: sqli
# @expected_line: 7
# @description: f-string 拼接 SQL execute 调用在同一行

import sqlite3

def search_users(name):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM users WHERE name = '{name}'")
    return cur.fetchall()
