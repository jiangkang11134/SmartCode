"""审查系统配置。

配置方式（环境变量）：
  MINICODE_REVIEW_MODE=off|loose|strict    — 审查模式（支持运行时切换）
  MINICODE_REVIEW_SUB_MODEL=model_name     — 子 Agent 模型覆盖

运行时切换说明：
  - off → loose/strict：触发全面回补扫描，检查已有代码 + 建 import map
  - 切换后立即生效，不需要重启进程
  - 切换通过 export MINICODE_REVIEW_MODE=strict 或 /review-mode strict 命令
"""

import os

# 向后兼容常量 —— 模块导入时快照的值
# 新代码应使用 get_review_mode() 以支持运行时切换
REVIEW_MODE = os.environ.get("MINICODE_REVIEW_MODE", "off").lower()

SUB_AGENT_MODEL = os.environ.get("MINICODE_REVIEW_SUB_MODEL", None)
SUB_AGENT_API_KEY = os.environ.get("MINICODE_REVIEW_SUB_API_KEY", None)
SUB_AGENT_API_BASE = os.environ.get("MINICODE_REVIEW_SUB_API_BASE", None)

FALSE_POSITIVE_PREFIXES = ("test_", "example_", "mock_", "fixture_", "sample_", "fake_")

IMPORT_MAP_DIR = ".mini-code-import-map"
IMPORT_MAP_FILE = "import-map.json"
REVIEW_FINDINGS_FILE = "review-findings.json"


def get_review_mode() -> str:
    """读取当前审查模式（每次调用读环境变量，支持运行时切换）。

    返回:
        "off" / "loose" / "strict"
    """
    return os.environ.get("MINICODE_REVIEW_MODE", "off").lower()
