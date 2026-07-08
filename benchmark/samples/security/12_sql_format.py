# @severity: critical
# @rule_id: sqli
# @expected_line: 7
# @description: .format() 拼接 SQL

def get_user_input(username):
    import sqlite3
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE username = '{}'".format(username)
    cur.execute(query)
    return cur.fetchall()
