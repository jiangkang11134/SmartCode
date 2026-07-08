"""
Quick validation script for the MiniCode review system.
Run with: python test_review_quick.py
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

passed = 0
failed = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}  -- {detail}")


print("=" * 60)
print("MiniCode 审查系统验证")
print("=" * 60)

# 1. Review module imports
print("\n--- 审查模块导入 ---")
try:
    from minicode.review.hooks import _pre_review_content, get_review_hooks, ReviewHooks
    check("from minicode.review.hooks import _pre_review_content", True)
except ImportError as e:
    check("minicode.review.hooks import", False, str(e))

try:
    from minicode.review.config import get_review_mode, FALSE_POSITIVE_PREFIXES, IMPORT_MAP_DIR
    check("from minicode.review.config import get_review_mode", True)
    mode = get_review_mode()
    check(f"get_review_mode() = '{mode}'", mode in ("off", "loose", "strict"))
    check(f"FALSE_POSITIVE_PREFIXES has {len(FALSE_POSITIVE_PREFIXES)} entries", len(FALSE_POSITIVE_PREFIXES) >= 5)
except ImportError as e:
    check("minicode.review.config import", False, str(e))

try:
    from minicode.review.memory import ReviewMemoryStore, ReviewFinding
    check("from minicode.review.memory import ReviewMemoryStore", True)
except ImportError as e:
    check("minicode.review.memory import", False, str(e))

try:
    from minicode.review.mode_engine import should_trigger_strict
    check("from minicode.review.mode_engine import should_trigger_strict", True)
except ImportError as e:
    check("minicode.review.mode_engine import", False, str(e))

try:
    from minicode.review.promotion import is_important_finding, promote_findings, promote_to_skill
    check("from minicode.review.promotion import promote_findings", True)
except ImportError as e:
    check("minicode.review.promotion import", False, str(e))

# 2. Import map
print("\n--- Import Map ---")
try:
    from minicode.tools.import_map import build_import_map, update_import_map_for_file, get_affected_files
    check("from minicode.tools.import_map import build_import_map", True)
except ImportError as e:
    check("minicode.tools.import_map import", False, str(e))

# Check import-map.json exists
import json
import_map_path = Path(".mini-code-import-map") / "import-map.json"
if import_map_path.exists():
    data = json.loads(import_map_path.read_text(encoding="utf-8"))
    sym_count = len(data.get("symbols", {}))
    check(f"import-map.json 存在，{sym_count} 个符号", sym_count > 0)
else:
    check("import-map.json 存在", False, "文件不存在")

# 3. 宽松审查（正则+AST检测）
print("\n--- 宽松审查：安全检测 ---")

# 3a. 硬编码密钥
issues = _pre_review_content('API_KEY = "sk-1234567890abcdef"', "test.py")
rules = [i["rule_id"] for i in issues]
check("硬编码密钥检测", "hardcoded-secret" in rules, f"got {rules}")

# 3b. 干净代码
issues = _pre_review_content("x = 1\ny = 2", "test.py")
check("干净代码无误报", len(issues) == 0, f"got {len(issues)} issues")

# 3c. eval
issues = _pre_review_content("result = eval(user_input)", "test.py")
rules = [i["rule_id"] for i in issues]
check("eval 检测", "unsafe-eval" in rules, f"got {rules}")

# 3d. SQL注入
issues = _pre_review_content('cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")', "test.py")
rules = [i["rule_id"] for i in issues]
check("SQL 注入检测 (f-string)", "sqli" in rules, f"got {rules}")

# 3e. TODO
issues = _pre_review_content("# TODO: implement this\nx = 1", "test.py")
rules = [i["rule_id"] for i in issues]
check("TODO 检测", "todo-left" in rules, f"got {rules}")

# 3f. 裸 except
issues = _pre_review_content("try:\n    do()\nexcept:\n    pass", "test.py")
rules = [i["rule_id"] for i in issues]
check("裸 except 检测", "bare-except" in rules, f"got {rules}")

# 3g. False positive 前缀跳过
issues = _pre_review_content('API_KEY = "sk-1234567890abcdef"', "test_mock_config.py")
check("FP 前缀跳过", len(issues) == 0, f"got {len(issues)} issues")

# 4. AGENT_TYPES
print("\n--- AGENT_TYPES 配置 ---")
from minicode.tools.task import AGENT_TYPES
check("AGENT_TYPES 包含 review", "review" in AGENT_TYPES)
check("AGENT_TYPES 包含 test", "test" in AGENT_TYPES)
rt = AGENT_TYPES["review"]
check(f"review: max_turns={rt['max_turns']}", rt["max_turns"] > 0)
check(f"review: 只读工具集", "read_file" in rt["allowed_tools"] and "write_file" not in rt["allowed_tools"])
tt = AGENT_TYPES["test"]
check(f"test: max_turns={tt['max_turns']}", tt["max_turns"] > 0)
check(f"test: 含 sandbox_test", "sandbox_test" in tt["allowed_tools"])

# 5. code_review re-export
print("\n--- code_review re-export ---")
try:
    from minicode.tools.code_review import _pre_review_content as cr_content
    check("code_review 末尾 re-export _pre_review_content", True)
except ImportError as e:
    check("code_review re-export", False, str(e))

# 6. 0. 钩子集成
print("\n--- 钩子集成 ---")
tool_exec_content = open("minicode/tool_executor.py", encoding="utf-8").read()
check("tool_executor.py: import get_review_hooks", "from minicode.review.hooks import get_review_hooks" in tool_exec_content)
check("tool_executor.py: on_before_write", "on_before_write" in tool_exec_content)
check("tool_executor.py: on_file_written", "on_file_written" in tool_exec_content)

loop_content = open("minicode/loop_orchestrator.py", encoding="utf-8").read()
check("loop_orchestrator.py: init_review_hooks", "init_review_hooks" in loop_content)
check("loop_orchestrator.py: on_turn_end", "on_turn_end" in loop_content)

# 7. mode_engine 严格触发
print("\n--- 严格审查触发 ---")
res, reason = should_trigger_strict("auth/login.py")
check(f"auth/login.py → 触发严格", res, reason)
res, reason = should_trigger_strict("utils/helper.py")
check(f"utils/helper.py → 不触发", not res, reason)
res, reason = should_trigger_strict("api/v1/payments.py")
check(f"api/v1/payments.py → 触发严格", res, reason)

# 8. 模式切换检测
print("\n--- 模式切换 ---")
from minicode.review.hooks import get_review_hooks
hooks = get_review_hooks(os.getcwd())
check("ReviewHooks 实例创建", hooks is not None)
check("on_before_write 存在", hasattr(hooks, "on_before_write"))
check("on_file_written 存在", hasattr(hooks, "on_file_written"))
check("on_turn_end 存在", hasattr(hooks, "on_turn_end"))
check("_check_transition 存在", hasattr(hooks, "_check_transition"))

# 总结
print("\n" + "=" * 60)
total = passed + failed
print(f"结果: {passed}/{total} 通过, {failed} 失败")
if failed == 0:
    print("✅ 审查系统完整性和功能验证全部通过！")
else:
    print(f"❌ {failed} 项测试失败")
print("=" * 60)