import os
import sys
import time
import uuid
from pathlib import Path

import requests


BACKEND_DIR = Path(__file__).resolve().parent
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

BASE_URL = os.getenv("CODEYAR_BASE_URL", "http://127.0.0.1:8000")
SCHOOL_ID = os.getenv("CODEYAR_SCHOOL_ID", "UOS")
PROFESSOR_USERNAME = os.getenv("CODEYAR_PROFESSOR_USERNAME", "judge0_professor")
STUDENT_USERNAME = os.getenv("CODEYAR_STUDENT_USERNAME", "judge0_student")
DEFAULT_PASSWORD = os.getenv("CODEYAR_TEST_PASSWORD", "pass1234")


PYTHON_CODE = """
import sys

data = sys.stdin.read().split()
a, b = map(int, data)
print(a + b)
"""


def request_json(method: str, path: str, *, token: str | None = None, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.setdefault("Content-Type", "application/json")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method,
        f"{BASE_URL}{path}",
        headers=headers,
        timeout=10,
        **kwargs,
    )
    return response


def ensure_school() -> None:
    response = request_json(
        "POST",
        "/api/v1/auth/schools",
        json={"id": SCHOOL_ID, "name": "University of Seoul", "code": SCHOOL_ID},
    )
    if response.status_code not in (201, 400):
        raise RuntimeError(f"school create failed: {response.status_code} {response.text}")


def ensure_user(username: str, role: str) -> None:
    response = request_json(
        "POST",
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": DEFAULT_PASSWORD,
            "role": role,
            "school_id": SCHOOL_ID,
        },
    )
    if response.status_code not in (201, 409):
        raise RuntimeError(f"{role} register failed: {response.status_code} {response.text}")


def login(username: str) -> str:
    response = request_json(
        "POST",
        "/api/v1/auth/login",
        json={"username": username, "password": DEFAULT_PASSWORD},
    )
    if response.status_code != 200:
        raise RuntimeError(f"login failed: {response.status_code} {response.text}")
    return response.json()["access_token"]


def ensure_seed_problem() -> str:
    configured_problem_id = os.getenv("CODEYAR_PROBLEM_ID")
    if configured_problem_id:
        return configured_problem_id

    from app.db.base import Base, SessionLocal, engine
    from app.models.exam import Exam
    from app.models.problem import Problem
    from app.models.school import School
    from app.models.user import User

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        school = db.query(School).filter(School.id == SCHOOL_ID).first()
        professor = db.query(User).filter(User.username == PROFESSOR_USERNAME).first()
        if not school or not professor:
            raise RuntimeError("school/professor seed is missing")

        exam = db.query(Exam).filter(Exam.title == "Judge0 Smoke Test").first()
        if not exam:
            exam = Exam(
                id=str(uuid.uuid4()),
                title="Judge0 Smoke Test",
                school_id=school.id,
                created_by=professor.id,
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)

        problem = db.query(Problem).filter(Problem.title == "Two Sum Smoke Test").first()
        if problem:
            return problem.id

        problem = Problem(
            id=str(uuid.uuid4()),
            exam_id=exam.id,
            title="Two Sum Smoke Test",
            description="Read two integers and print their sum.",
            time_limit=2.0,
            memory_limit=256,
            language_id=71,
            test_cases=(
                '[{"stdin":"1 2\\n","expected_output":"3\\n"},'
                '{"stdin":"100 200\\n","expected_output":"300\\n"},'
                '{"stdin":"-5 5\\n","expected_output":"0\\n"}]'
            ),
            ast_conditions=(
                '[{"action":"forbid","target":"import",'
                '"modules":["os","subprocess","socket","shutil"]},'
                '{"action":"forbid","target":"call","names":["eval","exec","__import__"]}]'
            ),
            global_ast_conditions="[]",
        )
        db.add(problem)
        db.commit()
        return problem.id
    finally:
        db.close()


def wait_for_result(submission_id: str, token: str) -> dict:
    for _ in range(30):
        time.sleep(1.5)
        response = request_json("GET", f"/api/v1/submissions/{submission_id}", token=token)
        if response.status_code != 200:
            raise RuntimeError(f"status fetch failed: {response.status_code} {response.text}")

        data = response.json()
        if data["status"] == "Pending":
            print("waiting for Judge0 result...")
            continue
        return data

    raise TimeoutError("submission stayed Pending for too long")


def run_test() -> None:
    print("checking Judge0 health...")
    health = request_json("GET", "/api/v1/submissions/judge0/health")
    print(f"Judge0 health: {health.status_code} {health.text}")

    ensure_school()
    ensure_user(PROFESSOR_USERNAME, "professor")
    ensure_user(STUDENT_USERNAME, "student")
    login(PROFESSOR_USERNAME)
    student_token = login(STUDENT_USERNAME)
    problem_id = ensure_seed_problem()

    print(f"submitting problem_id={problem_id}")
    response = request_json(
        "POST",
        "/api/v1/submissions/",
        token=student_token,
        json={"problem_id": problem_id, "code": PYTHON_CODE},
    )
    if response.status_code != 202:
        raise RuntimeError(f"submit failed: {response.status_code} {response.text}")

    submission_id = response.json()["submission_id"]
    print(f"submission accepted: {submission_id}")

    result = wait_for_result(submission_id, student_token)
    print(f"final status: {result['status']}")
    print(f"passed: {result['passed']}")
    print(f"score: {result['score']}")
    print(f"passed tests: {result['passed_count']}/{result['total_count']}")
    if result.get("error_reason"):
        print(f"error_reason: {result['error_reason']}")

    for index, case in enumerate(result["results"], start=1):
        print(
            f"case {index}: {case['status_desc']} "
            f"time={case['time']}s memory={case['memory']}KB stdout={case['stdout']!r}"
        )


if __name__ == "__main__":
    try:
        run_test()
    except requests.exceptions.ConnectionError:
        print("server connection failed. Start uvicorn first: uvicorn app.main:app --reload")
        raise
