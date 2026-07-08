# @severity: critical
# @rule_id: sqli
# @expected_line: 7
# @description: .format() 拼接用户输入到 SQL

import sqlite3

def search(user_input):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE name = '{}'".format(user_input)
    cur.execute(query)
    return cur.fetchall()
