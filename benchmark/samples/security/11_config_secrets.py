# @severity: critical
# @rule_id: hardcoded-secret
# @expected_line: 2
# @description: 配置文件中直接写密钥

DATABASE_URL = "postgresql://admin:pass123@localhost:5432/prod"
REDIS_PASSWORD = "redis-secret-789"
JWT_SECRET = "jwt-signing-key-001"
