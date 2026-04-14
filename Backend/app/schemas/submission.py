from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from app.services.judge import TestCaseInput, SubmissionResult

class SubmitRequest(BaseModel):
    code: str = Field(..., description="The user's source code to be executed")
    language_id: int = Field(71, description="Language of the source code (71=Python 3.8.1)")
    test_cases: List[TestCaseInput] = Field(..., description="테스트 케이스 모음")
    time_limit: float = Field(2.0, description="Execution time limit in seconds")
    ast_conditions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="문제별 실행 전 코드 구조 검사 조건",
    )
    global_ast_conditions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="전역 공통 코드 구조 검사 조건",
    )

class SubmitResponse(BaseModel):
    submission_id: str
    status: str
    message: Optional[str] = None

class SubmissionStatusResponse(BaseModel):
    status: str
    results: List[SubmissionResult]
    message: Optional[str] = None
