import json
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.problem import Problem
from app.models.submission import Submission as SubmissionModel
from app.schemas.submission import (
    SubmitRequest, SubmitResponse,
    SubmissionStatusResponse, TestCaseResult, Judge0HealthResponse,
)
from app.services.ast_checker import ASTConfigurationError, check_phase1_conditions
from app.services.judge import (
    Judge0Client,
    Judge0APIError,
    TestCaseInput,
    SubmissionResult,
    calculate_score,
)

router = APIRouter()
judge_client = Judge0Client()


def _load_json_list(raw: str | None, field_name: str) -> list:
    try:
        value = json.loads(raw or "[]")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"{field_name} JSON 형식이 올바르지 않습니다.")

    if not isinstance(value, list):
        raise HTTPException(status_code=400, detail=f"{field_name}은 JSON 배열이어야 합니다.")

    return value


@router.post("/", response_model=SubmitResponse, status_code=202)
async def submit_code(
    request: SubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    코드 제출 엔드포인트.
    - JWT에서 user_id를 자동 추출
    - DB에서 problem 조회 → test_cases, ast_conditions 읽기
    - AST 검사 후 Judge0에 제출
    """
    # 1) 문제 조회
    problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="존재하지 않는 문제 ID입니다.")

    # 2) DB에서 AST 조건, 테스트케이스 읽기
    ast_conditions = _load_json_list(problem.ast_conditions, "ast_conditions")
    global_ast_conditions = _load_json_list(problem.global_ast_conditions, "global_ast_conditions")
    test_cases_raw = _load_json_list(problem.test_cases, "test_cases")
    try:
        test_cases = [TestCaseInput(**tc) for tc in test_cases_raw]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"test_cases 형식이 올바르지 않습니다: {e}")

    if not test_cases:
        raise HTTPException(status_code=400, detail="이 문제에 등록된 테스트케이스가 없습니다.")

    # 3) AST 검사
    try:
        ast_result = check_phase1_conditions(
            code=request.code,
            problem_conditions=ast_conditions,
            global_conditions=global_ast_conditions,
        )
    except ASTConfigurationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    submission_id = str(uuid.uuid4())

    if not ast_result.passed:
        # AST 실패 → Judge0에 보내지 않고 즉시 기록
        submission = SubmissionModel(
            id=submission_id,
            user_id=current_user.id,
            problem_id=request.problem_id,
            code=request.code,
            language_id=problem.language_id,
            status="AST Fail",
            passed=False,
            error_reason=f"AST Fail: {ast_result.message}",
        )
        db.add(submission)
        db.commit()

        return SubmitResponse(
            submission_id=submission_id,
            status="AST Fail",
            message=ast_result.message,
        )

    # 4) Judge0에 제출
    try:
        tokens_str = await judge_client.submit_batch(
            source_code=request.code,
            language_id=problem.language_id,
            test_cases=test_cases,
            time_limit=problem.time_limit,
            memory_limit=problem.memory_limit,
        )
    except Judge0APIError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 5) DB에 Submission 레코드 생성
    submission = SubmissionModel(
        id=submission_id,
        user_id=current_user.id,
        problem_id=request.problem_id,
        code=request.code,
        language_id=problem.language_id,
        status="Pending",
    )
    db.add(submission)
    db.commit()

    # 6) 백그라운드 폴링 워커 투입
    background_tasks.add_task(judge_client.poll_and_update, tokens_str, submission_id)

    return SubmitResponse(submission_id=submission_id, status="Pending")


@router.get("/judge0/health", response_model=Judge0HealthResponse)
async def get_judge0_health():
    """
    프론트/백엔드 통합 전 Judge0 연결 상태를 확인하는 엔드포인트입니다.
    """
    return await judge_client.health_check()


@router.get("/{submission_id}", response_model=SubmissionStatusResponse)
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    채점 결과 조회 엔드포인트.
    로그인한 사용자 본인의 제출만 조회 가능합니다.
    """
    submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # 본인 제출만 조회 가능
    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인의 제출만 조회할 수 있습니다.")

    # problem → exam_id 조회
    problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
    exam_id = problem.exam_id if problem else ""

    # result_json 파싱
    results = []
    if submission.result_json:
        try:
            results = [TestCaseResult(**r) for r in json.loads(submission.result_json)]
        except (json.JSONDecodeError, TypeError):
            results = []
    score_results = [SubmissionResult(**r.model_dump()) for r in results]
    total_count, passed_count, score = calculate_score(score_results)

    return SubmissionStatusResponse(
        submission_id=submission.id,
        user_id=submission.user_id,
        exam_id=exam_id,
        problem_id=submission.problem_id,
        status=submission.status,
        passed=submission.passed,
        error_reason=submission.error_reason,
        results=results,
        total_count=total_count,
        passed_count=passed_count,
        score=score,
        submitted_at=submission.submitted_at.isoformat() if submission.submitted_at else None,
    )
