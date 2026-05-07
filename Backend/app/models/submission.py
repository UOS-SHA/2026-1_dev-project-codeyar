from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey

from app.db.base import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    problem_id = Column(String, ForeignKey("problems.id"), nullable=False)
    code = Column(Text, nullable=False)
    language_id = Column(Integer, default=71)
    status = Column(String, default="Pending")          # Pending / Completed / Timeout / Error / AST Fail
    passed = Column(Boolean, nullable=True)              # True=전체 통과, False=실패, None=채점 중
    error_reason = Column(String, nullable=True)         # 실패 사유 문자열
    result_json = Column(Text, nullable=True)            # 각 테스트케이스 결과 JSON
    submitted_at = Column(DateTime, default=datetime.utcnow)
