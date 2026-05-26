import unittest

from app.services.ast_checker import (
    ASTConfigurationError,
    check_ast_conditions,
    check_phase1_conditions,
    merge_conditions,
)


class ASTCheckerTests(unittest.TestCase):
    def test_require_function_and_forbid_loop_passes(self) -> None:
        code = """
def fibo(n):
    if n <= 1:
        return n
    return fibo(n - 1) + fibo(n - 2)
"""
        result = check_phase1_conditions(
            code,
            problem_conditions=[
                {"action": "require", "target": "function", "name": "fibo"},
                {"action": "require", "target": "recursion", "in_function": "fibo"},
                {"action": "forbid", "target": "loop"},
            ],
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.message, "OK")

    def test_forbid_loop_fails_with_default_message(self) -> None:
        code = """
def fibo(n):
    for i in range(n):
        print(i)
"""
        result = check_phase1_conditions(
            code,
            problem_conditions=[{"action": "forbid", "target": "loop"}],
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.message, "반복문 사용이 금지되어 있습니다")

    def test_method_requirement_detects_class_members(self) -> None:
        code = """
class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)
"""
        result = check_phase1_conditions(
            code,
            problem_conditions=[
                {"action": "require", "target": "class", "name": "Stack"},
                {"action": "require", "target": "method", "class_name": "Stack", "name": "push"},
            ],
        )
        self.assertTrue(result.passed)

    def test_call_and_import_rules_use_normalized_names(self) -> None:
        code = """
from collections import deque

def bfs():
    queue = deque([1, 2, 3])
    return queue.popleft()
"""
        result = check_phase1_conditions(
            code,
            problem_conditions=[
                {"action": "require", "target": "import", "modules": ["collections"]},
                {"action": "require", "target": "call", "names": ["deque", "popleft"]},
            ],
        )
        self.assertTrue(result.passed)

    def test_syntax_error_returns_failed_result(self) -> None:
        result = check_phase1_conditions(
            "def broken(:\n    return 1\n",
            problem_conditions=[{"action": "require", "target": "function", "name": "broken"}],
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.failed_condition, {"target": "syntax"})

    def test_no_conditions_skip_python_parse(self) -> None:
        result = check_phase1_conditions("public class Main {")
        self.assertTrue(result.passed)

    def test_legacy_plan_condition_format_is_supported(self) -> None:
        passed, message = check_ast_conditions(
            """
def fibo(n):
    if n <= 1:
        return n
    return fibo(n - 1)
""",
            [
                {"type": "function_exists", "name": "fibo"},
                {"type": "recursive_call", "function": "fibo"},
                {"type": "forbidden_call", "names": ["eval", "exec"]},
            ],
        )
        self.assertTrue(passed)
        self.assertEqual(message, "OK")

    def test_forbidden_dotted_call_detects_import_alias(self) -> None:
        result = check_phase1_conditions(
            """
import os as operating_system

def run():
    return operating_system.system("echo unsafe")
""",
            problem_conditions=[
                {"action": "forbid", "target": "call", "names": ["os.system"]},
            ],
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.message, "함수 'os.system' 사용이 금지되어 있습니다")

    def test_dotted_call_rule_does_not_match_unrelated_tail_name(self) -> None:
        result = check_phase1_conditions(
            """
def system(command):
    return command

system("local helper")
""",
            problem_conditions=[
                {"action": "forbid", "target": "call", "names": ["os.system"]},
            ],
        )
        self.assertTrue(result.passed)

    def test_nested_function_inside_method_is_not_reported_as_method(self) -> None:
        code = """
class Stack:
    def push(self, value):
        def helper():
            return value
        return helper()
"""
        result = check_phase1_conditions(
            code,
            problem_conditions=[
                {"action": "require", "target": "method", "class_name": "Stack", "name": "helper"},
            ],
        )
        self.assertFalse(result.passed)

    def test_invalid_condition_raises_configuration_error(self) -> None:
        with self.assertRaises(ASTConfigurationError):
            check_phase1_conditions(
                "print('hello')",
                problem_conditions=[{"action": "require", "target": "loop", "kind": "until"}],
            )

    def test_merge_conditions_prefers_problem_specific_rules(self) -> None:
        merged = merge_conditions(
            global_conditions=[{"action": "forbid", "target": "loop", "kind": "any"}],
            problem_conditions=[{"action": "require", "target": "loop", "kind": "any"}],
        )
        self.assertEqual(merged, [{"action": "require", "target": "loop", "kind": "any"}])


if __name__ == "__main__":
    unittest.main()
