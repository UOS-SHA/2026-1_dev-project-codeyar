import ast
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Set, Tuple


Condition = Mapping[str, Any]


DEFAULT_MESSAGES: Dict[Tuple[str, str], str] = {
    ("require", "function"): "함수 '{name}'이(가) 정의되지 않았습니다",
    ("require", "class"): "클래스 '{name}'이(가) 정의되지 않았습니다",
    ("require", "method"): "클래스 '{class_name}'에 메서드 '{name}'이(가) 없습니다",
    ("require", "recursion"): "함수 '{in_function}'에서 재귀 호출이 필요합니다",
    ("require", "loop"): "반복문을 사용해야 합니다",
    ("require", "call"): "함수 {names}을(를) 사용해야 합니다",
    ("require", "import"): "모듈 {modules}을(를) import해야 합니다",
    ("forbid", "function"): "함수 '{name}' 정의가 금지되어 있습니다",
    ("forbid", "class"): "클래스 '{name}' 정의가 금지되어 있습니다",
    ("forbid", "method"): "클래스 '{class_name}'의 메서드 '{name}' 사용이 금지되어 있습니다",
    ("forbid", "recursion"): "재귀 호출이 금지되어 있습니다",
    ("forbid", "loop"): "반복문 사용이 금지되어 있습니다",
    ("forbid", "call"): "함수 {names} 사용이 금지되어 있습니다",
    ("forbid", "import"): "모듈 {modules} import가 금지되어 있습니다",
}


class ASTConfigurationError(ValueError):
    pass


@dataclass
class FunctionInfo:
    name: str
    param_count: int
    has_direct_recursion: bool = False


@dataclass
class ASTCheckResult:
    passed: bool
    message: str = "OK"
    failed_condition: Optional[Dict[str, Any]] = None


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, Set[str]] = {}
        self.imports: Set[str] = set()
        self.calls: Set[str] = set()
        self.has_for_loop = False
        self.has_while_loop = False
        self._class_stack: List[str] = []
        self._function_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.setdefault(node.name, set())
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._register_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._register_function(node)

    def _register_function(self, node: Any) -> None:
        param_count = len(node.args.posonlyargs) + len(node.args.args) + len(node.args.kwonlyargs)
        if node.args.vararg is not None:
            param_count += 1
        if node.args.kwarg is not None:
            param_count += 1

        info = FunctionInfo(name=node.name, param_count=param_count)
        self.functions.setdefault(node.name, info)

        if self._class_stack:
            self.classes.setdefault(self._class_stack[-1], set()).add(node.name)

        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_For(self, node: ast.For) -> None:
        self.has_for_loop = True
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.has_while_loop = True
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._record_import(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._record_import(node.module)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _get_call_name(node.func)
        if call_name:
            self.calls.add(call_name)
            if self._function_stack and _is_direct_recursion(call_name, self._function_stack[-1]):
                self.functions[self._function_stack[-1]].has_direct_recursion = True
        self.generic_visit(node)

    def _record_import(self, module_name: str) -> None:
        self.imports.add(module_name)
        if "." in module_name:
            parts = module_name.split(".")
            for index in range(1, len(parts)):
                self.imports.add(".".join(parts[:index]))


def _get_call_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _get_call_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr
    return None


def _is_direct_recursion(call_name: str, function_name: str) -> bool:
    if call_name == function_name:
        return True
    if call_name.endswith(f".{function_name}"):
        return True
    return False


def _values_to_display(values: Iterable[str]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def _condition_key(condition: Condition) -> Tuple[str, ...]:
    key_parts = [str(condition["target"])]
    for field_name in ("name", "class_name", "in_function", "kind"):
        if field_name in condition:
            key_parts.append(str(condition[field_name]))
    for field_name in ("names", "modules"):
        if field_name in condition:
            values = sorted(str(value) for value in condition[field_name])
            key_parts.append(",".join(values))
    return tuple(key_parts)


def merge_conditions(
    global_conditions: Optional[List[Dict[str, Any]]],
    problem_conditions: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    merged: Dict[Tuple[str, ...], Dict[str, Any]] = {}
    for condition in global_conditions or []:
        merged[_condition_key(condition)] = dict(condition)
    for condition in problem_conditions or []:
        merged[_condition_key(condition)] = dict(condition)
    return list(merged.values())


def check_phase1_conditions(
    code: str,
    problem_conditions: Optional[List[Dict[str, Any]]] = None,
    global_conditions: Optional[List[Dict[str, Any]]] = None,
) -> ASTCheckResult:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        line = exc.lineno or 0
        column = exc.offset or 0
        return ASTCheckResult(
            passed=False,
            message=f"문법 오류가 있습니다 (line {line}, column {column}): {exc.msg}",
            failed_condition={"target": "syntax"},
        )

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    conditions = merge_conditions(global_conditions, problem_conditions)
    for raw_condition in conditions:
        condition = _normalize_condition(raw_condition)
        passed = _evaluate_condition(analyzer, condition)
        if not passed:
            return ASTCheckResult(
                passed=False,
                message=_build_message(condition),
                failed_condition=dict(condition),
            )

    return ASTCheckResult(passed=True)


def _normalize_condition(condition: Condition) -> Dict[str, Any]:
    normalized = dict(condition)
    action = normalized.get("action")
    target = normalized.get("target")

    if action not in {"require", "forbid"}:
        raise ASTConfigurationError(f"지원하지 않는 action입니다: {action}")
    if target not in {"function", "class", "method", "recursion", "loop", "call", "import"}:
        raise ASTConfigurationError(f"Phase 1에서 지원하지 않는 target입니다: {target}")

    if target in {"function", "class"} and "name" not in normalized:
        raise ASTConfigurationError(f"target='{target}'에는 'name'이 필요합니다")
    if target == "method" and ("class_name" not in normalized or "name" not in normalized):
        raise ASTConfigurationError("target='method'에는 'class_name'과 'name'이 필요합니다")
    if target == "recursion" and "in_function" not in normalized:
        raise ASTConfigurationError("target='recursion'에는 'in_function'이 필요합니다")
    if target == "loop":
        normalized["kind"] = normalized.get("kind", "any")
        if normalized["kind"] not in {"for", "while", "any"}:
            raise ASTConfigurationError(f"지원하지 않는 loop kind입니다: {normalized['kind']}")
    if target == "call":
        names = normalized.get("names")
        if not isinstance(names, list) or not names:
            raise ASTConfigurationError("target='call'에는 비어있지 않은 'names' 리스트가 필요합니다")
    if target == "import":
        modules = normalized.get("modules")
        if not isinstance(modules, list) or not modules:
            raise ASTConfigurationError("target='import'에는 비어있지 않은 'modules' 리스트가 필요합니다")

    return normalized


def _evaluate_condition(analyzer: CodeAnalyzer, condition: Dict[str, Any]) -> bool:
    action = condition["action"]
    target = condition["target"]

    if target == "function":
        matched = _match_function(analyzer, condition)
    elif target == "class":
        matched = condition["name"] in analyzer.classes
    elif target == "method":
        methods = analyzer.classes.get(condition["class_name"], set())
        matched = condition["name"] in methods
    elif target == "recursion":
        info = analyzer.functions.get(condition["in_function"])
        matched = info is not None and info.has_direct_recursion
    elif target == "loop":
        matched = _match_loop(analyzer, condition["kind"])
    elif target == "call":
        matched = _match_any_name(condition["names"], analyzer.calls)
    elif target == "import":
        matched = _match_any_module(condition["modules"], analyzer.imports)
    else:
        raise ASTConfigurationError(f"알 수 없는 target입니다: {target}")

    return matched if action == "require" else not matched


def _match_function(analyzer: CodeAnalyzer, condition: Dict[str, Any]) -> bool:
    info = analyzer.functions.get(condition["name"])
    if info is None:
        return False

    min_params = condition.get("min_params")
    max_params = condition.get("max_params")
    if min_params is not None and info.param_count < min_params:
        return False
    if max_params is not None and info.param_count > max_params:
        return False
    return True


def _match_loop(analyzer: CodeAnalyzer, kind: str) -> bool:
    if kind == "for":
        return analyzer.has_for_loop
    if kind == "while":
        return analyzer.has_while_loop
    return analyzer.has_for_loop or analyzer.has_while_loop


def _match_any_name(expected_names: List[str], actual_names: Set[str]) -> bool:
    for expected in expected_names:
        if any(_name_matches(expected, actual) for actual in actual_names):
            return True
    return False


def _name_matches(expected: str, actual: str) -> bool:
    if expected == actual:
        return True
    expected_tail = expected.split(".")[-1]
    actual_tail = actual.split(".")[-1]
    if expected_tail == actual_tail:
        return True
    if actual.endswith(f".{expected}"):
        return True
    return False


def _match_any_module(expected_modules: List[str], actual_modules: Set[str]) -> bool:
    for expected in expected_modules:
        if expected in actual_modules:
            return True
        if any(module.startswith(f"{expected}.") for module in actual_modules):
            return True
    return False


def _build_message(condition: Dict[str, Any]) -> str:
    if condition.get("message"):
        return str(condition["message"])

    template = DEFAULT_MESSAGES.get((condition["action"], condition["target"]))
    if template is None:
        raise ASTConfigurationError(
            f"메시지 템플릿이 없는 조건입니다: {condition['action']}/{condition['target']}"
        )

    context = dict(condition)
    if "names" in context:
        context["names"] = _values_to_display(context["names"])
    if "modules" in context:
        context["modules"] = _values_to_display(context["modules"])
    return template.format(**context)
