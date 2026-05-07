from pydantic import BaseModel, Field
from typing import List, Optional


class SubmitRequest(BaseModel):
    """코드 제출 요청 — problem_id와 code만 보냄. test_cases는 DB에서 읽음."""
    problem_id: str = Field(..., description="제출할 문제 ID")
    code: str = Field(..., description="사용자 소스 코드")


class SubmitResponse(BaseModel):
    submission_id: str
    status: str
    message: Optional[str] = None


class TestCaseResult(BaseModel):
    """각 테스트케이스의 채점 결과"""
    status_id: int
    status_desc: str        # "Accepted", "Wrong Answer", "Time Limit Exceeded" 등
    time: float
    memory: int
    stdout: str
    stderr: str


class SubmissionStatusResponse(BaseModel):
    """채점 결과 조회 응답"""
    submission_id: str
    user_id: str
    exam_id: str
    problem_id: str
    status: str                          # "Pending" / "Completed" / "Timeout" / "Error" / "AST Fail"
    passed: Optional[bool] = None        # True=전체 통과, False=실패, None=채점 중
    error_reason: Optional[str] = None   # 실패 사유
    results: List[TestCaseResult] = []   # 각 테스트케이스 상세 결과
    submitted_at: Optional[str] = None
