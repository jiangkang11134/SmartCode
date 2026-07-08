"""
Ultra-minimal test for the review system (pytest style).
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from minicode.review.hooks import _pre_review_content, get_review_hooks, ReviewHooks
from minicode.review.config import get_review_mode
from minicode.review.memory import ReviewMemoryStore, ReviewFinding
from minicode.review.mode_engine import should_trigger_strict
from minicode.review.promotion import is_important_finding, promote_findings
from minicode.tools.task import AGENT_TYPES


def test_imports():
    assert _pre_review_content is not None
    assert get_review_hooks is not None
    assert ReviewHooks is not None
    assert get_review_mode() in ("off", "loose", "strict")
    assert ReviewMemoryStore is not None
    assert should_trigger_strict is not None
    assert is_important_finding is not None
    assert "review" in AGENT_TYPES
    assert "test" in AGENT_TYPES


def test_hardcoded_secret():
    issues = _pre_review_content('API_KEY = "sk-1234567890abcdef"', "test.py")
    rules = [i["rule_id"] for i in issues]
    assert "hardcoded-secret" in rules


def test_clean_code():
    issues = _pre_review_content("x = 1\ny = 2", "test.py")
    assert len(issues) == 0


def test_unsafe_eval():
    issues = _pre_review_content("result = eval(user_input)", "test.py")
    assert "unsafe-eval" in [i["rule_id"] for i in issues]


def test_sql_injection():
    issues = _pre_review_content('cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")', "test.py")
    assert "sqli" in [i["rule_id"] for i in issues]


def test_todo():
    issues = _pre_review_content("# TODO: implement this\nx = 1", "test.py")
    assert "todo-left" in [i["rule_id"] for i in issues]


def test_bare_except():
    issues = _pre_review_content("try:\n    do()\nexcept:\n    pass\n", "test.py")
    assert "bare-except" in [i["rule_id"] for i in issues]


def test_fp_prefix_skip():
    issues = _pre_review_content('API_KEY = "sk-1234567890abcdef"', "test_fixture.py")
    assert len(issues) == 0


def test_mode_engine_auth():
    r, _ = should_trigger_strict("auth/login.py")
    assert r

def test_mode_engine_utils():
    r, _ = should_trigger_strict("utils/helpers.py")
    assert not r

def test_mode_engine_api():
    r, _ = should_trigger_strict("api/v1/endpoint.py")
    assert r

def test_mode_engine_diff():
    r, _ = should_trigger_strict("main.py", diff_stat={"changed_lines": 300})
    assert r


def test_hooks_factory():
    hooks = get_review_hooks(os.getcwd())
    assert isinstance(hooks, ReviewHooks)
    assert hasattr(hooks, "on_before_write")
    assert hasattr(hooks, "on_file_written")
    assert hasattr(hooks, "on_turn_end")


def test_memory():
    store = ReviewMemoryStore()
    finding = ReviewFinding(severity="critical", file_path="test.py", rule_id="test", title="test")
    store.add_finding(finding)
    assert finding.id is not None


def test_promotion_security():
    r = is_important_finding({"severity": "critical", "rule_id": "hardcoded-secret", "description": "test"})
    assert r == "skill"


def test_promotion_arch():
    r = is_important_finding({"severity": "major", "rule_id": "arch-service", "description": "test"})
    assert r == "global_memory"


def test_agent_types_review_config():
    rt = AGENT_TYPES["review"]
    assert rt["max_turns"] > 0
    assert "read_file" in rt["allowed_tools"]
    assert "write_file" not in rt["allowed_tools"]


def test_agent_types_test_config():
    tt = AGENT_TYPES["test"]
    assert tt["max_turns"] > 0
    assert "sandbox_test" in tt["allowed_tools"]


def test_code_review_reexport():
    import importlib
    mod = importlib.import_module("minicode.tools.code_review")
    assert hasattr(mod, "_pre_review_content")


def test_tool_executor_integration():
    content = open("minicode/tool_executor.py", encoding="utf-8").read()
    assert "on_before_write" in content
    assert "on_file_written" in content


def test_loop_orchestrator_integration():
    content = open("minicode/loop_orchestrator.py", encoding="utf-8").read()
    assert "on_turn_end" in content


def test_import_map_exists():
    import json
    path = Path(".mini-code-import-map") / "import-map.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "symbols" in data
    assert len(data["symbols"]) > 0


def test_review_dir():
    assert os.path.isdir("minicode/review")
    files = os.listdir("minicode/review")
    expected = {"__init__.py", "config.py", "hooks.py", "memory.py", "mode_engine.py", "promotion.py"}
    for f in expected:
        assert f in files, f"Missing {f}"