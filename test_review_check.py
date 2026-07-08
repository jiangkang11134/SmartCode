"""Quick test for the review system — pytest style."""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def test_import_review_hooks():
    from minicode.review.hooks import _pre_review_content, get_review_hooks, ReviewHooks
    assert _pre_review_content is not None
    assert get_review_hooks is not None
    assert ReviewHooks is not None


def test_import_review_config():
    from minicode.review.config import get_review_mode, FALSE_POSITIVE_PREFIXES, IMPORT_MAP_DIR
    mode = get_review_mode()
    assert mode in ("off", "loose", "strict")
    assert isinstance(FALSE_POSITIVE_PREFIXES, tuple)
    assert IMPORT_MAP_DIR == ".mini-code-import-map"


def test_pre_review_hardcoded_secret():
    from minicode.review.hooks import _pre_review_content
    content = '''API_KEY = "sk-1234567890abcdef"
password = "super_secret_123"
def safe():
    return 42
'''
    issues = _pre_review_content(content, "test.py")
    rules = [i["rule_id"] for i in issues]
    assert "hardcoded-secret" in rules, f"Expected hardcoded-secret, got {rules}"


def test_pre_review_clean_code():
    from minicode.review.hooks import _pre_review_content
    content = '''import os
from pathlib import Path

def greet(name: str) -> str:
    return f"Hello, {name}"
'''
    issues = _pre_review_content(content, "clean.py")
    assert len(issues) == 0, f"Expected no issues, got {issues}"


def test_pre_review_eval():
    from minicode.review.hooks import _pre_review_content
    content = 'result = eval(user_input)'
    issues = _pre_review_content(content, "test.py")
    rules = [i["rule_id"] for i in issues]
    assert "unsafe-eval" in rules, f"Expected unsafe-eval, got {rules}"


def test_pre_review_sql_injection():
    from minicode.review.hooks import _pre_review_content
    content = 'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")'
    issues = _pre_review_content(content, "test.py")
    rules = [i["rule_id"] for i in issues]
    assert "sqli" in rules, f"Expected sqli, got {rules}"


def test_pre_review_todo():
    from minicode.review.hooks import _pre_review_content
    content = '# TODO: implement proper error handling\nx = 1'
    issues = _pre_review_content(content, "test.py")
    rules = [i["rule_id"] for i in issues]
    assert "todo-left" in rules, f"Expected todo-left, got {rules}"


def test_pre_review_bare_except():
    from minicode.review.hooks import _pre_review_content
    content = '''try:
    do_something()
except:
    pass
'''
    issues = _pre_review_content(content, "test.py")
    rules = [i["rule_id"] for i in issues]
    assert "bare-except" in rules, f"Expected bare-except, got {rules}"


def test_false_positive_prefix_skip():
    from minicode.review.hooks import _pre_review_content
    content = 'API_KEY = "sk-1234567890abcdef"'
    issues = _pre_review_content(content, "test_fixture.py")
    assert len(issues) == 0, f"Expected false positive skip, got {issues}"


def test_import_map_functions():
    from minicode.tools.import_map import build_import_map, update_import_map_for_file, get_affected_files, _extract_symbols
    assert build_import_map is not None
    assert update_import_map_for_file is not None
    assert get_affected_files is not None
    assert _extract_symbols is not None


def test_code_review_re_export():
    from minicode.tools.code_review import _pre_review_content
    assert _pre_review_content is not None


def test_agent_types_have_review_test():
    from minicode.tools.task import AGENT_TYPES
    assert "review" in AGENT_TYPES, f"AGENT_TYPES missing review: {list(AGENT_TYPES.keys())}"
    assert "test" in AGENT_TYPES, f"AGENT_TYPES missing test: {list(AGENT_TYPES.keys())}"
    rt = AGENT_TYPES["review"]
    assert rt["max_turns"] > 0
    assert rt["allowed_tools"] is not None
    assert "read_file" in rt["allowed_tools"]
    assert "write_file" not in rt["allowed_tools"]
    tt = AGENT_TYPES["test"]
    assert tt["max_turns"] > 0
    assert tt["allowed_tools"] is not None


def test_review_memory():
    from minicode.review.memory import ReviewMemoryStore, ReviewFinding
    store = ReviewMemoryStore()
    assert store is not None
    stats = store.get_stats()
    assert "total" in stats
    assert "by_severity" in stats
    assert "by_status" in stats


def test_mode_engine():
    from minicode.review.mode_engine import should_trigger_strict
    result, reason = should_trigger_strict("auth/login.py")
    assert result == True, f"Expected strict for auth/, got {result}, {reason}"
    result2, reason2 = should_trigger_strict("utils/helper.py")
    assert result2 == False, f"Expected no strict for utils/, got {result2}, {reason2}"
    result3, reason3 = should_trigger_strict("api/endpoint.py")
    assert result3 == True, f"Expected strict for api/, got {result3}, {reason3}"
    result4, reason4 = should_trigger_strict("security/token.py")
    assert result4 == True, f"Expected strict for security/, got {result4}, {reason4}"


def test_promotion_module():
    from minicode.review.promotion import is_important_finding, promote_findings, promote_to_skill
    assert is_important_finding is not None
    assert promote_findings is not None
    assert promote_to_skill is not None


def test_review_hooks_factory():
    from minicode.review.hooks import get_review_hooks, ReviewHooks
    hooks = get_review_hooks(os.getcwd())
    assert hooks is not None
    assert isinstance(hooks, ReviewHooks)
    assert hasattr(hooks, "on_before_write")
    assert hasattr(hooks, "on_file_written")
    assert hasattr(hooks, "on_turn_end")


def test_import_map_exists():
    import json
    path = Path(".mini-code-import-map") / "import-map.json"
    assert path.exists(), f"import-map.json not found at {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "version" in data
    assert "symbols" in data
    assert "updated_at" in data
    symbols = data.get("symbols", {})
    # Check that it has some symbols from the review system
    assert len(symbols) > 0, f"import-map.json has 0 symbols"


def test_hooks_in_tool_executor():
    content = open("minicode/tool_executor.py", encoding="utf-8").read()
    assert "from minicode.review.hooks import get_review_hooks" in content
    assert "on_before_write" in content
    assert "on_file_written" in content


def test_hooks_in_loop_orchestrator():
    content = open("minicode/loop_orchestrator.py", encoding="utf-8").read()
    assert "init_review_hooks" in content
    assert "on_turn_end" in content