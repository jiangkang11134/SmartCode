"""
Ultra-minimal test for the review system.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

errors = []

def t(name, ok, msg=""):
    if ok:
        print(f"  OK  {name}")
    else:
        print(f"  FAIL  {name}: {msg}")
        errors.append(name)

# 1. Imports
from minicode.review.hooks import _pre_review_content, get_review_hooks, ReviewHooks
t("import hooks", True)

from minicode.review.config import get_review_mode, FALSE_POSITIVE_PREFIXES
t("import config", True)
t("get_review_mode()", get_review_mode() in ("off", "loose", "strict"))

from minicode.review.memory import ReviewMemoryStore, ReviewFinding
t("import memory", True)

from minicode.review.mode_engine import should_trigger_strict
t("import mode_engine", True)

from minicode.review.promotion import is_important_finding, promote_findings
t("import promotion", True)

from minicode.tools.import_map import build_import_map, update_import_map_for_file, get_affected_files
t("import import_map", True)

from minicode.tools.task import AGENT_TYPES
t("AGENT_TYPES has review", "review" in AGENT_TYPES)
t("AGENT_TYPES has test", "test" in AGENT_TYPES)

from minicode.tools.code_review import _pre_review_content as cr_export
import minicode.tools.code_review as cr_mod
t("code_review re-exports _pre_review_content", "_pre_review_content" in dir(cr_mod))

# 2. Pre-review content checks
issues = _pre_review_content('API_KEY = "sk-1234567890abcdef"', "test.py")
t("hardcoded-secret detected", "hardcoded-secret" in [i["rule_id"] for i in issues])

issues = _pre_review_content("x = 1\ny = 2", "test.py")
t("clean code no issues", len(issues) == 0, f"got {len(issues)}")

issues = _pre_review_content("result = eval(user_input)", "test.py")
t("unsafe-eval detected", "unsafe-eval" in [i["rule_id"] for i in issues])

issues = _pre_review_content('cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")', "test.py")
t("sqli detected", "sqli" in [i["rule_id"] for i in issues])

issues = _pre_review_content("# TODO: implement this\nx = 1", "test.py")
t("todo-left detected", "todo-left" in [i["rule_id"] for i in issues])

issues = _pre_review_content("try:\n    do()\nexcept:\n    pass\n", "test.py")
t("bare-except detected", "bare-except" in [i["rule_id"] for i in issues])

# 3. FP prefix skip
issues = _pre_review_content('API_KEY = "sk-1234567890abcdef"', "test_fixture.py")
t("FP prefix skip", len(issues) == 0, f"got {len(issues)}")

# 4. Mode engine
r, _ = should_trigger_strict("auth/login.py")
t("auth path triggers strict", r)
r, _ = should_trigger_strict("utils/helpers.py")
t("utils path no trigger", not r)
r, _ = should_trigger_strict("api/v1/endpoint.py")
t("api path triggers strict", r)
r, _ = should_trigger_strict("payment/processor.py")
t("payment path triggers strict", r)
r, _ = should_trigger_strict("main.py", diff_stat={"changed_lines": 300})
t("big diff triggers strict", r)
r, _ = should_trigger_strict("main.py", diff_stat={"touched_files": 15})
t("many files triggers strict", r)

# 5. ReviewHooks
hooks = get_review_hooks(os.getcwd())
t("hooks factory returns ReviewHooks", isinstance(hooks, ReviewHooks))
t("has on_before_write", hasattr(hooks, "on_before_write"))
t("has on_file_written", hasattr(hooks, "on_file_written"))
t("has on_turn_end", hasattr(hooks, "on_turn_end"))

# 6. Memory
store = ReviewMemoryStore()
t("memory store created", store is not None)
finding = ReviewFinding(severity="critical", file_path="test.py", rule_id="hardcoded-secret", title="test")
store.add_finding(finding)
t("finding added", finding.id is not None)

# 7. Promotion
finding = {"severity": "critical", "rule_id": "hardcoded-secret", "description": "test"}
t("security -> skill", is_important_finding(finding) == "skill")
finding = {"severity": "minor", "rule_id": "style", "description": "test"}
t("minor -> None", is_important_finding(finding) is None)
finding = {"severity": "major", "rule_id": "arch-service", "description": "test"}
t("arch -> global_memory", is_important_finding(finding) == "global_memory")

from collections import Counter
finding = {"severity": "major", "rule_id": "bare-except", "description": "test"}
t("freq>=3 -> skill", is_important_finding(finding, Counter({"bare-except": 3})) == "skill")

# 8. Integration points
content = open("minicode/tool_executor.py", encoding="utf-8").read()
t("tool_executor has review hooks import", "from minicode.review.hooks import get_review_hooks" in content)
t("tool_executor has on_before_write", "on_before_write" in content)
t("tool_executor has on_file_written", "on_file_written" in content)

content = open("minicode/loop_orchestrator.py", encoding="utf-8").read()
t("loop_orchestrator has init_review_hooks", "init_review_hooks" in content)
t("loop_orchestrator has on_turn_end", "on_turn_end" in content)

# 9. Import map exists
import json
path = Path(".mini-code-import-map") / "import-map.json"
t("import-map.json exists", path.exists())
if path.exists():
    data = json.loads(path.read_text(encoding="utf-8"))
    t("has symbols", len(data.get("symbols", {})) > 0, f"0 symbols")

# 10. Review directory completeness
assert os.path.isdir("minicode/review")
files = os.listdir("minicode/review")
expected = {"__init__.py", "config.py", "hooks.py", "memory.py", "mode_engine.py", "promotion.py"}
for f in expected:
    t(f"review/{f} exists", f in files, f"missing {f}")

# Summary
print(f"\n{'='*50}")
total = 28 + len(expected) + 5
passed = total - len(errors)
print(f"Passed: {passed}/{total}")
if errors:
    print(f"Failed: {len(errors)}: {errors}")
else:
    print("ALL PASSED!")