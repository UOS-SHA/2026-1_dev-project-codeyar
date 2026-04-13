from pydantic import BaseModel, Field
from typing import List
from app.services.judge import TestCaseInput, SubmissionResult

class SubmitRequest(BaseModel):
    code: str = Field(..., description="The user's source code to be executed")
    language_id: int = Field(71, description="Language of the source code (71=Python 3.8.1)")
    test_cases: List[TestCaseInput] = Field(..., description="테스트 케이스 모음")
    time_limit: float = Field(2.0, description="Execution time limit in seconds")

class SubmitResponse(BaseModel):
    submission_id: str
    status: str

class SubmissionStatusResponse(BaseModel):
    status: str
    results: List[SubmissionResult]
