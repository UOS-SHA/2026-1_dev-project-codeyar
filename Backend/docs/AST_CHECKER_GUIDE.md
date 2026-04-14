# AST Checker — 코드 구조 검사 모듈 가이드

> **파일 위치**: `Backend/app/services/ast_checker.py`
> **최종 수정**: 2026-04-14

---

## 1. 개요

`ast_checker`는 학생이 제출한 Python 코드가 **교수가 설정한 구조적 요구사항**을 만족하는지
코드를 **실행하지 않고** 정적으로 검사하는 모듈입니다.

Python 표준 라이브러리 `ast`(Abstract Syntax Tree)를 사용하여 코드를 파싱한 뒤,
함수·클래스·반복문·재귀·함수 호출·import 등의 존재 여부를 검증합니다.

### 왜 필요한가?

| 시나리오 | 설명 |
|---|---|
| 재귀 과제 | "반드시 재귀로 구현하세요" → `for`/`while` 금지, 재귀 호출 필수 |
| OOP 과제 | "클래스 `Stack`을 정의하고 `push`, `pop` 메서드를 구현하세요" |
| 라이브러리 제한 | "외부 모듈 사용 금지" → 특정 import 금지 |
| 함수 시그니처 강제 | "함수 `solution`은 인자 2개를 받아야 합니다" |

---

## 2. 시스템 내 위치 (파이프라인)

```
[학생 코드 제출]
      │
      ▼
┌─────────────────────┐
│  Phase 1: AST 검사  │  ← ast_checker.py (이 모듈)
│  (실행 전 정적 분석)  │
└────────┬────────────┘
         │ 통과 시
         ▼
┌─────────────────────┐
│  Phase 2: Judge0    │  ← judge.py
│  (실제 실행 & 채점)   │
└─────────────────────┘
```

- AST 검사에 **실패**하면 Judge0에 코드를 보내지 않고 즉시 `"AST Fail"` 응답을 반환합니다.
- AST 검사에 **통과**하면 Judge0 배치 제출 → 백그라운드 폴링 → 채점 결과 저장 흐름으로 진행됩니다.

---

## 3. 핵심 함수

### `check_phase1_conditions(code, problem_conditions, global_conditions)`

**메인 진입점**입니다. 모든 AST 검사는 이 함수를 호출하여 수행합니다.

```python
from app.services.ast_checker import check_phase1_conditions

result = check_phase1_conditions(
    code="def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)",
    problem_conditions=[
        {"action": "require", "target": "function", "name": "factorial"},
        {"action": "require", "target": "recursion", "in_function": "factorial"},
    ],
    global_conditions=[
        {"action": "forbid", "target": "import", "modules": ["os", "subprocess"]},
    ],
)

print(result.passed)    # True
print(result.message)   # "OK"
```

#### 매개변수

| 매개변수 | 타입 | 설명 |
|---|---|---|
| `code` | `str` | 검사할 Python 소스 코드 문자열 |
| `problem_conditions` | `List[Dict]` (optional) | **문제별** 검사 조건 리스트 |
| `global_conditions` | `List[Dict]` (optional) | **전역 공통** 검사 조건 리스트 |

#### 반환값: `ASTCheckResult`

| 필드 | 타입 | 설명 |
|---|---|---|
| `passed` | `bool` | 모든 조건을 통과했으면 `True` |
| `message` | `str` | 통과 시 `"OK"`, 실패 시 한국어 오류 메시지 |
| `failed_condition` | `Dict` or `None` | 실패한 조건의 원본 딕셔너리 (디버깅용) |

#### 조건 병합 규칙

- `global_conditions`가 먼저 적용되고, `problem_conditions`가 뒤에 병합됩니다.
- **동일한 조건 키**(target + name 등의 조합)가 중복되면, `problem_conditions`의 값이 우선합니다.
- 이를 통해 "전역은 `os` import 금지, 특정 문제에서는 허용"과 같은 오버라이드가 가능합니다.

---

## 4. 조건(Condition) 포맷

모든 조건은 아래 공통 구조를 따르는 JSON 딕셔너리입니다:

```json
{
  "action": "require" | "forbid",
  "target": "<검사 대상>",
  ...추가 필드
}
```

- **`action`**: `"require"` (반드시 있어야 함) 또는 `"forbid"` (있으면 안 됨)
- **`target`**: 검사 대상 종류 (아래 표 참조)
- **`message`** *(선택)*: 실패 시 표시할 커스텀 메시지. 생략하면 기본 한국어 템플릿을 사용합니다.

---

## 5. 지원하는 Target 타입 상세

### 5.1 `function` — 함수 정의 검사

특정 이름의 함수가 정의되어 있는지 확인합니다. 선택적으로 파라미터 개수도 검증할 수 있습니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `name` | ✅ | `str` | 함수 이름 |
| `min_params` | ❌ | `int` | 최소 파라미터 수 |
| `max_params` | ❌ | `int` | 최대 파라미터 수 |

**파라미터 수 계산**: positional-only + positional-or-keyword + keyword-only + `*args`(1) + `**kwargs`(1)

```json
// "solution 함수를 반드시 정의하고, 파라미터는 정확히 2개여야 합니다"
{
  "action": "require",
  "target": "function",
  "name": "solution",
  "min_params": 2,
  "max_params": 2
}
```

```json
// "helper 함수 정의를 금지합니다"
{
  "action": "forbid",
  "target": "function",
  "name": "helper"
}
```

---

### 5.2 `class` — 클래스 정의 검사

특정 이름의 클래스가 정의되어 있는지 확인합니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `name` | ✅ | `str` | 클래스 이름 |

```json
// "Stack 클래스가 반드시 정의되어야 합니다"
{
  "action": "require",
  "target": "class",
  "name": "Stack"
}
```

---

### 5.3 `method` — 클래스 내 메서드 검사

특정 클래스 안에 특정 메서드가 정의되어 있는지 확인합니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `class_name` | ✅ | `str` | 대상 클래스 이름 |
| `name` | ✅ | `str` | 메서드 이름 |

```json
// "Stack 클래스에 push 메서드가 반드시 있어야 합니다"
{
  "action": "require",
  "target": "method",
  "class_name": "Stack",
  "name": "push"
}
```

---

### 5.4 `recursion` — 재귀 호출 검사

특정 함수 내에서 **직접 재귀**(자기 자신을 호출)가 사용되는지 확인합니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `in_function` | ✅ | `str` | 재귀 감지 대상 함수 이름 |

> ⚠️ **주의**: 직접 재귀(direct recursion)만 감지합니다. `A → B → A`와 같은 상호 재귀(mutual recursion)는 감지하지 않습니다.

```json
// "factorial 함수에서 반드시 재귀를 사용해야 합니다"
{
  "action": "require",
  "target": "recursion",
  "in_function": "factorial"
}
```

```json
// "fibonacci 함수에서 재귀 사용을 금지합니다 (반복문으로 구현하세요)"
{
  "action": "forbid",
  "target": "recursion",
  "in_function": "fibonacci"
}
```

---

### 5.5 `loop` — 반복문 검사

`for`문, `while`문, 또는 둘 다의 사용 여부를 검사합니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `kind` | ❌ | `"for"` \| `"while"` \| `"any"` | 반복문 종류 (기본값: `"any"`) |

```json
// "반복문을 사용하면 안 됩니다 (재귀로 풀어야 하는 문제)"
{
  "action": "forbid",
  "target": "loop"
}
```

```json
// "while문을 반드시 사용해야 합니다"
{
  "action": "require",
  "target": "loop",
  "kind": "while"
}
```

> **참고**: `kind`를 생략하면 `"any"`로 처리됩니다. `"any"`는 `for` 또는 `while` 중 하나라도 있으면 매칭됩니다.

---

### 5.6 `call` — 함수 호출 검사

코드에서 특정 함수/메서드를 호출하는지 확인합니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `names` | ✅ | `List[str]` | 검사할 함수/메서드 이름 리스트 (하나라도 매칭되면 통과) |

**이름 매칭 규칙** (유연한 매칭):
- `"print"` → `print()` 직접 호출에 매칭
- `"sort"` → `list.sort()`, `my_list.sort()` 등 끝 이름이 같으면 매칭
- `"math.sqrt"` → `math.sqrt()` 호출에 매칭

```json
// "sorted() 또는 .sort()를 반드시 사용해야 합니다"
{
  "action": "require",
  "target": "call",
  "names": ["sorted", "sort"]
}
```

```json
// "eval()이나 exec() 사용을 금지합니다"
{
  "action": "forbid",
  "target": "call",
  "names": ["eval", "exec"]
}
```

---

### 5.7 `import` — 모듈 Import 검사

특정 모듈의 import 여부를 확인합니다.

| 필드 | 필수 | 타입 | 설명 |
|---|---|---|---|
| `modules` | ✅ | `List[str]` | 검사할 모듈 이름 리스트 (하나라도 매칭되면 통과) |

**모듈 매칭 규칙**:
- `"os"` → `import os`, `import os.path`, `from os import listdir` 모두 매칭
- `"numpy"` → `import numpy`, `import numpy.linalg` 매칭
- 하위 모듈(`os.path`)도 상위 모듈(`os`)로 자동 등록됩니다.

```json
// "math 모듈을 반드시 import 해야 합니다"
{
  "action": "require",
  "target": "import",
  "modules": ["math"]
}
```

```json
// "os, subprocess 모듈 사용을 금지합니다"
{
  "action": "forbid",
  "target": "import",
  "modules": ["os", "subprocess", "shutil"]
}
```

---

## 6. API 연동 방법

### HTTP 요청 예시 (POST `/api/v1/submissions/`)

```json
{
  "code": "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)\n\nprint(factorial(int(input())))",
  "language_id": 71,
  "time_limit": 2.0,
  "test_cases": [
    {"stdin": "5\n", "expected_output": "120\n"},
    {"stdin": "0\n", "expected_output": "1\n"}
  ],
  "ast_conditions": [
    {"action": "require", "target": "function", "name": "factorial"},
    {"action": "require", "target": "recursion", "in_function": "factorial"},
    {"action": "forbid", "target": "loop"}
  ],
  "global_ast_conditions": [
    {"action": "forbid", "target": "import", "modules": ["os", "subprocess"]}
  ]
}
```

### 요청 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `ast_conditions` | `List[Dict]` | 해당 문제 고유의 AST 검사 조건 |
| `global_ast_conditions` | `List[Dict]` | 모든 문제에 공통 적용되는 AST 검사 조건 |

### AST 실패 시 응답 (HTTP 202)

```json
{
  "submission_id": "abc-123-...",
  "status": "AST Fail",
  "message": "반복문 사용이 금지되어 있습니다"
}
```

### AST 통과 시 응답 (HTTP 202)

```json
{
  "submission_id": "def-456-...",
  "status": "Pending",
  "message": null
}
```

---

## 7. 문법 오류 처리

코드에 Python 문법 오류가 있으면 AST 파싱 자체가 실패합니다.
이 경우 조건 검사 없이 즉시 실패를 반환합니다.

```python
result = check_phase1_conditions(code="def foo(:")
# result.passed == False
# result.message == "문법 오류가 있습니다 (line 1, column 9): invalid syntax"
# result.failed_condition == {"target": "syntax"}
```

---

## 8. 에러 처리: `ASTConfigurationError`

조건 JSON의 형식이 잘못되었을 때 발생하는 예외입니다.
API 레이어에서 HTTP 400으로 변환됩니다.

| 상황 | 에러 메시지 예시 |
|---|---|
| `action`이 `require`/`forbid`가 아님 | `지원하지 않는 action입니다: must` |
| `target`이 지원되지 않는 값 | `Phase 1에서 지원하지 않는 target입니다: variable` |
| `function`/`class`에 `name` 누락 | `target='function'에는 'name'이 필요합니다` |
| `method`에 `class_name` 또는 `name` 누락 | `target='method'에는 'class_name'과 'name'이 필요합니다` |
| `recursion`에 `in_function` 누락 | `target='recursion'에는 'in_function'이 필요합니다` |
| `call`에 `names` 누락 또는 빈 리스트 | `target='call'에는 비어있지 않은 'names' 리스트가 필요합니다` |
| `import`에 `modules` 누락 또는 빈 리스트 | `target='import'에는 비어있지 않은 'modules' 리스트가 필요합니다` |
| `loop`의 `kind`가 잘못됨 | `지원하지 않는 loop kind입니다: do_while` |

---

## 9. 실전 조건 조합 예시

### 예시 A: 재귀 과제

> "함수 `fibonacci`를 재귀로 구현하세요. 반복문 사용 금지."

```json
[
  {"action": "require", "target": "function", "name": "fibonacci", "min_params": 1},
  {"action": "require", "target": "recursion", "in_function": "fibonacci"},
  {"action": "forbid", "target": "loop"}
]
```

### 예시 B: OOP 과제

> "클래스 `LinkedList`를 정의하고 `append`, `remove`, `__len__` 메서드를 구현하세요."

```json
[
  {"action": "require", "target": "class", "name": "LinkedList"},
  {"action": "require", "target": "method", "class_name": "LinkedList", "name": "append"},
  {"action": "require", "target": "method", "class_name": "LinkedList", "name": "remove"},
  {"action": "require", "target": "method", "class_name": "LinkedList", "name": "__len__"}
]
```

### 예시 C: 라이브러리 제한 + 정렬 함수 사용 강제

> "built-in `sorted()`를 사용하지 말고 직접 정렬 함수를 구현하세요. numpy 사용 금지."

```json
[
  {"action": "forbid", "target": "call", "names": ["sorted"]},
  {"action": "forbid", "target": "import", "modules": ["numpy"]},
  {"action": "require", "target": "function", "name": "my_sort"}
]
```

### 예시 D: 커스텀 에러 메시지

```json
[
  {
    "action": "require",
    "target": "function",
    "name": "solution",
    "message": "solution() 함수를 반드시 정의해주세요! (가이드 3페이지 참고)"
  }
]
```

---

## 10. 내부 구조 요약 (개발자 참고용)

```
check_phase1_conditions()        ← 진입점
  ├─ ast.parse(code)             ← 문법 오류 감지
  ├─ CodeAnalyzer.visit(tree)    ← AST 순회하며 정보 수집
  ├─ merge_conditions()          ← global + problem 조건 병합
  └─ for each condition:
       ├─ _normalize_condition() ← 유효성 검증 + 기본값 설정
       ├─ _evaluate_condition()  ← 조건 판정 (require→있어야함, forbid→없어야함)
       └─ _build_message()       ← 실패 시 한국어 메시지 생성
```

### `CodeAnalyzer` — AST 순회 결과

| 속성 | 타입 | 설명 |
|---|---|---|
| `functions` | `Dict[str, FunctionInfo]` | 정의된 함수명 → 정보 (파라미터 수, 재귀 여부) |
| `classes` | `Dict[str, Set[str]]` | 클래스명 → 메서드 이름 집합 |
| `imports` | `Set[str]` | import된 모듈 이름 집합 (하위 모듈도 상위로 자동 등록) |
| `calls` | `Set[str]` | 호출된 함수/메서드 이름 집합 |
| `has_for_loop` | `bool` | for문 존재 여부 |
| `has_while_loop` | `bool` | while문 존재 여부 |

---

## 11. 제한 사항 및 주의 사항

1. **직접 재귀만 감지**: `A() → B() → A()`와 같은 간접/상호 재귀는 감지하지 않습니다.
2. **동적 호출 미감지**: `getattr(obj, "method")()` 같은 동적 호출은 AST 분석으로 잡을 수 없습니다.
3. **변수 별칭 미추적**: `f = print; f("hello")`에서 `print` 호출을 감지하지 못합니다.
4. **전역 스코프 한정 아님**: 코드 전체에서 검색합니다. "top-level에서만 정의된 함수"와 같은 스코프 구분은 하지 않습니다.
5. **`async def` 지원**: 비동기 함수 정의도 일반 함수와 동일하게 처리합니다.
