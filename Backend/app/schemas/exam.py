from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 시험 생성 시 프론트엔드에서 받을 데이터 체계
class ExamCreate(BaseModel):
    id: str
    title: str
    school_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

# API가 결과를 리턴해줄 때 쓸 체계
class ExamResponse(ExamCreate):
    created_by: str

    class Config:
        from_attributes = True