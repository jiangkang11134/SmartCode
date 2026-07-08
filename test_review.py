"""Quick test for the review system."""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Test 1: Import review module
try:
    from minicode.review.hooks import _pre_review_content
    from minicode.review.config import get_review_mode
    print(f"[PASS] Import _pre_review_content OK")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: get_review_mode
mode = get_review_mode()
print(f"[PASS] get_review_mode() = {mode}")

# Test 3: Pre-review check on a hardcoded secret
test_content = """API_KEY = "sk-1234567890abcdef"
password = "super_secret_123"
def safe_function():
    return 42
"""
issues = _pre_review_content(test_content, "test.py")
print(f"[INFO] Security test: {len(issues)} issues found")
for i in issues:
    print(f"  L{i['line']} [{i['severity']}] {i['rule_id']}: {i['message']}")

# Test 4: Pre-review check on clean code
clean = """import os
from pathlib import Path

def greet(name: str) -> str:
    return f"Hello, {name}"
"""
issues = _pre_review_content(clean, "clean.py")
print(f"[INFO] Clean code test: {len(issues)} issues (expect 0)")
if len(issues) == 0:
    print("[PASS] No false positives on clean code")
else:
    print(f"[FAIL] Unexpected issues: {issues}")

# Test 5: Test import map
try:
    from minicode.tools.import_map import build_import_map, update_import_map_for_file, get_affected_files
    print("[PASS] Import map functions loaded OK")
except ImportError as e:
    print(f"[FAIL] Import map import failed: {e}")

# Test 6: Check that code_review re-exports
try:
    from minicode.tools.code_review import _pre_review_content
    print("[PASS] code_review re-exports _pre_review_content")
except ImportError as e:
    print(f"[FAIL] code_review re-export failed: {e}")

# Test 7: Check AGENT_TYPES
try:
    from minicode.tools.task import AGENT_TYPES
    if "review" in AGENT_TYPES and "test" in AGENT_TYPES:
        print(f"[PASS] AGENT_TYPES has review and test")
        rt = AGENT_TYPES["review"]
        tt = AGENT_TYPES["test"]
        print(f"  review: allowed_tools={len(rt['allowed_tools'])}, max_turns={rt['max_turns']}")
        print(f"  test: allowed_tools={len(tt['allowed_tools'])}, max_turns={tt['max_turns']}")
    else:
        print(f"[FAIL] AGENT_TYPES missing review or test. Keys: {list(AGENT_TYPES.keys())}")
except ImportError as e:
    print(f"[FAIL] AGENT_TYPES import failed: {e}")

# Test 8: Check review memory
try:
    from minicode.review.memory import ReviewMemoryStore, ReviewFinding
    print("[PASS] ReviewMemoryStore loaded OK")
    store = ReviewMemoryStore()
    print(f"[PASS] ReviewMemoryStore created")
    stats = store.get_stats()
    print(f"  Stats: {stats}")
except ImportError as e:
    print(f"[FAIL] ReviewMemoryStore import failed: {e}")

# Test 9: Check mode_engine
try:
    from minicode.review.mode_engine import should_trigger_strict
    print("[PASS] should_trigger_strict loaded OK")
    result, reason = should_trigger_strict("auth/login.py")
    print(f"  auth/login.py: should_trigger={result}, reason={reason}")
    result2, reason2 = should_trigger_strict("utils/helper.py")
    print(f"  utils/helper.py: should_trigger={result2}, reason={reason2}")
except ImportError as e:
    print(f"[FAIL] mode_engine import failed: {e}")

# Test 10: Check promotion
try:
    from minicode.review.promotion import is_important_finding, promote_findings
    print("[PASS] promotion module loaded OK")
except ImportError as e:
    print(f"[FAIL] promotion import failed: {e}")

print("\n=== All checks complete ===")