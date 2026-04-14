"""
예시 A: 재귀 과제 — 실제 검사 결과 확인 스크립트
조건:
  - fibonacci 함수가 반드시 정의되어야 함 (파라미터 1개 이상)
  - fibonacci 함수 내에서 재귀 호출 필수
  - 반복문(for/while) 사용 금지

실행:
  cd Backend && python docs/run_examples.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.ast_checker import check_phase1_conditions

CONDITIONS = [
    {"action": "require", "target": "function", "name": "fibonacci", "min_params": 1},
    {"action": "require", "target": "recursion", "in_function": "fibonacci"},
    {"action": "forbid",  "target": "loop"},
]

PASS_CASES = {
    "✅ 통과 1 — 기본 재귀 구현": """\
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(int(input())))
""",

    "✅ 통과 2 — 메모이제이션(재귀 + dict)": """\
memo = {}

def fibonacci(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n - 1) + fibonacci(n - 2)
    return memo[n]

print(fibonacci(int(input())))
""",

    "✅ 통과 3 — 클래스 내부에 정의된 재귀 함수": """\
class Solver:
    def fibonacci(self, n):
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)

s = Solver()
print(s.fibonacci(int(input())))
""",
}

FAIL_CASES = {
    "❌ 실패 1 — fibonacci 함수 자체가 없음": """\
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(int(input())))
""",

    "❌ 실패 2 — 재귀 없이 for문으로 구현": """\
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(fibonacci(int(input())))
""",

    "❌ 실패 3 — 재귀 없이 while문으로 구현": """\
def fibonacci(n):
    a, b = 0, 1
    while n > 0:
        a, b = b, a + b
        n -= 1
    return a

print(fibonacci(int(input())))
""",

    "❌ 실패 4 — 재귀는 있지만 반복문도 사용": """\
def fibonacci(n):
    # 재귀 + 반복문 혼용
    if n <= 1:
        return n
    results = []
    for i in range(n):
        results.append(fibonacci(i))
    return results[-1] + results[-2]

print(fibonacci(int(input())))
""",

    "❌ 실패 5 — 파라미터가 0개 (min_params=1 위반)": """\
def fibonacci():
    pass
""",

    "❌ 실패 6 — 문법 오류": """\
def fibonacci(n)
    return fibonacci(n-1) + fibonacci(n-2)
""",
}


def run_all():
    sep = "─" * 62

    print(f"\n{'═'*62}")
    print("  예시 A — 재귀 과제 AST 검사 실행 결과")
    print(f"{'═'*62}\n")
    print("  조건:")
    for c in CONDITIONS:
        print(f"    {c}")
    print()

    # ---------- 통과 케이스 ----------
    print(f"{sep}")
    print("  [ 통과 케이스 ]")
    print(f"{sep}")
    for label, code in PASS_CASES.items():
        result = check_phase1_conditions(code, problem_conditions=CONDITIONS)
        status = "PASS ✅" if result.passed else "FAIL ❌"
        print(f"\n  {label}")
        print(f"  결과  : {status}")
        print(f"  메시지: {result.message}")
        if result.failed_condition:
            print(f"  실패조건: {result.failed_condition}")
    print()

    # ---------- 실패 케이스 ----------
    print(f"{sep}")
    print("  [ 실패 케이스 ]")
    print(f"{sep}")
    for label, code in FAIL_CASES.items():
        result = check_phase1_conditions(code, problem_conditions=CONDITIONS)
        status = "FAIL ❌" if not result.passed else "PASS ✅ (예상과 다름!)"
        print(f"\n  {label}")
        print(f"  결과  : {status}")
        print(f"  메시지: {result.message}")
        if result.failed_condition:
            print(f"  실패조건: {result.failed_condition}")
    print(f"\n{'═'*62}\n")


if __name__ == "__main__":
    run_all()
