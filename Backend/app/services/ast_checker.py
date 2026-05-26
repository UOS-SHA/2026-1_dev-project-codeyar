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
        self.import_aliases: Dict[str, str] = {}
        self.calls: Set[str] = set()
        self.has_for_loop = False
        self.has_while_loop = False
        self._class_stack: List[Tuple[str, int]] = []
        self._function_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.setdefault(node.name, set())
        self._class_stack.append((node.name, len(self._function_stack)))
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

        if self._class_stack and len(self._function_stack) == self._class_stack[-1][1]:
            class_name = self._class_stack[-1][0]
            self.classes.setdefault(class_name, set()).add(node.name)

        self._function_stack.append(node.name)
        self.generic_visit(node)
        self._function_stack.pop()

    def visit_For(self, node: ast.For) -> None:
        self.has_for_loop = True
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.has_for_loop = True
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self.has_for_loop = True
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.has_while_loop = True
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._record_import(alias.name)
            bound_name = alias.asname or alias.name.split(".", 1)[0]
            target_name = alias.name if alias.asname else alias.name.split(".", 1)[0]
            self.import_aliases[bound_name] = target_name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._record_import(node.module)
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound_name = alias.asname or alias.name
                self.import_aliases[bound_name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _get_call_name(node.func)
        if call_name:
            self.calls.add(call_name)
            resolved_name = self._resolve_call_alias(call_name)
            self.calls.add(resolved_name)
            if self._function_stack and _is_direct_recursion(call_name, self._function_stack[-1]):
                self.functions[self._function_stack[-1]].has_direct_recursion = True
        self.generic_visit(node)

    def _record_import(self, module_name: str) -> None:
        self.imports.add(module_name)
        if "." in module_name:
            parts = module_name.split(".")
            for index in range(1, len(parts)):
                self.imports.add(".".join(parts[:index]))

    def _resolve_call_alias(self, call_name: str) -> str:
        parts = call_name.split(".")
        root = parts[0]
        resolved_root = self.import_aliases.get(root)
        if not resolved_root:
            return call_name
        if len(parts) == 1:
            return resolved_root
        return ".".join([resolved_root, *parts[1:]])


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
        normalized = _normalize_condition(condition)
        merged[_condition_key(normalized)] = normalized
    for condition in problem_conditions or []:
        normalized = _normalize_condition(condition)
        merged[_condition_key(normalized)] = normalized
    return list(merged.values())


def check_phase1_conditions(
    code: str,
    problem_conditions: Optional[List[Dict[str, Any]]] = None,
    global_conditions: Optional[List[Dict[str, Any]]] = None,
) -> ASTCheckResult:
    conditions = merge_conditions(global_conditions, problem_conditions)
    if not conditions:
        return ASTCheckResult(passed=True)

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

    for condition in conditions:
        passed = _evaluate_condition(analyzer, condition)
        if not passed:
            return ASTCheckResult(
                passed=False,
                message=_build_message(condition),
                failed_condition=dict(condition),
            )

    return ASTCheckResult(passed=True)


def check_ast_conditions(code: str, conditions: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, str]:
    """
    Backward-compatible wrapper for the initial implementation plan.
    Prefer check_phase1_conditions() when the caller needs failed_condition details.
    """
    result = check_phase1_conditions(code=code, problem_conditions=conditions)
    return result.passed, result.message


def _normalize_condition(condition: Condition) -> Dict[str, Any]:
    normalized = _translate_legacy_condition(condition)
    action = normalized.get("action")
    target = normalized.get("target")

    if action not in {"require", "forbid"}:
        raise ASTConfigurationError(f"지원하지 않는 action입니다: {action}")
    if target not in {"function", "class", "method", "recursion", "loop", "call", "import"}:
        raise ASTConfigurationError(f"Phase 1에서 지원하지 않는 target입니다: {target}")

    if target in {"function", "class"}:
        _require_text_field(normalized, "name", target)
    if target == "method":
        _require_text_field(normalized, "class_name", target)
        _require_text_field(normalized, "name", target)
    if target == "recursion":
        _require_text_field(normalized, "in_function", target)

    if target == "function":
        _validate_param_limit(normalized, "min_params")
        _validate_param_limit(normalized, "max_params")
        min_params = normalized.get("min_params")
        max_params = normalized.get("max_params")
        if min_params is not None and max_params is not None and min_params > max_params:
            raise ASTConfigurationError("min_params는 max_params보다 클 수 없습니다")
    if target == "loop":
        normalized["kind"] = normalized.get("kind", "any")
        if normalized["kind"] not in {"for", "while", "any"}:
            raise ASTConfigurationError(f"지원하지 않는 loop kind입니다: {normalized['kind']}")
    if target == "call":
        normalized["names"] = _validate_text_list(normalized.get("names"), "names", target)
    if target == "import":
        normalized["modules"] = _validate_text_list(normalized.get("modules"), "modules", target)

    return normalized


def _translate_legacy_condition(condition: Condition) -> Dict[str, Any]:
    normalized = dict(condition)
    condition_type = normalized.pop("type", None)
    if condition_type is None:
        return normalized

    if condition_type == "function_exists":
        normalized["action"] = "require"
        normalized["target"] = "function"
        return normalized
    if condition_type == "class_exists":
        normalized["action"] = "require"
        normalized["target"] = "class"
        return normalized
    if condition_type == "method_exists":
        class_name = normalized.pop("class", None)
        if class_name is not None:
            normalized["class_name"] = class_name
        normalized["action"] = "require"
        normalized["target"] = "method"
        return normalized
    if condition_type == "recursive_call":
        function_name = normalized.pop("function", None) or normalized.pop("name", None)
        if function_name is not None:
            normalized["in_function"] = function_name
        normalized["action"] = "require"
        normalized["target"] = "recursion"
        return normalized
    if condition_type == "forbidden_call":
        normalized["action"] = "forbid"
        normalized["target"] = "call"
        return normalized
    if condition_type == "required_call":
        normalized["action"] = "require"
        normalized["target"] = "call"
        return normalized
    if condition_type == "forbidden_import":
        normalized["action"] = "forbid"
        normalized["target"] = "import"
        return normalized
    if condition_type == "required_import":
        normalized["action"] = "require"
        normalized["target"] = "import"
        return normalized

    raise ASTConfigurationError(f"지원하지 않는 condition type입니다: {condition_type}")


def _require_text_field(condition: Dict[str, Any], field_name: str, target: str) -> None:
    value = condition.get(field_name)
    if not isinstance(value, str) or not value:
        if target == "method":
            raise ASTConfigurationError("target='method'에는 'class_name'과 'name'이 필요합니다")
        if target == "recursion":
            raise ASTConfigurationError("target='recursion'에는 'in_function'이 필요합니다")
        raise ASTConfigurationError(f"target='{target}'에는 'name'이 필요합니다")


def _validate_param_limit(condition: Dict[str, Any], field_name: str) -> None:
    if field_name not in condition:
        return
    value = condition[field_name]
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ASTConfigurationError(f"{field_name}은 0 이상의 정수여야 합니다")


def _validate_text_list(value: Any, field_name: str, target: str) -> List[str]:
    if not isinstance(value, list) or not value:
        raise ASTConfigurationError(f"target='{target}'에는 비어있지 않은 '{field_name}' 리스트가 필요합니다")
    if not all(isinstance(item, str) and item for item in value):
        raise ASTConfigurationError(f"target='{target}'의 '{field_name}'에는 문자열만 사용할 수 있습니다")
    return value


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

    if "." in expected:
        return actual.endswith(f".{expected}")

    expected_tail = expected
    actual_tail = actual.split(".")[-1]
    if expected_tail == actual_tail:
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
