from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# 문제 생성 시 프론트엔드에서 받을 데이터 체계
class ProblemCreate(BaseModel):
    id: str
    exam_id: str
    title: str
    description: Optional[str] = None
    time_limit: Optional[float] = 2.0
    memory_limit: Optional[int] = 256
    language_id: Optional[int] = 71
    # 프론트엔드에서는 Python 리스트/딕셔너리 형태로 편하게 받고, DB에 넣을 때 문자열로 바꿀 겁니다.
    ast_conditions: Optional[List[Any]] = []
    global_ast_conditions: Optional[List[Any]] = []
    test_cases: Optional[List[Dict[str, Any]]] = []

# API 응답용 체계
class ProblemResponse(BaseModel):
    id: str
    exam_id: str
    title: str
    description: Optional[str] = None
    time_limit: float
    memory_limit: int
    language_id: int

    class Config:
        from_attributes = True