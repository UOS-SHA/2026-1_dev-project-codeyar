from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey

from app.db.base import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String, primary_key=True)
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    time_limit = Column(Float, default=2.0)               # 초 단위
    memory_limit = Column(Integer, default=256)            # MB 단위
    language_id = Column(Integer, default=71)              # Judge0 언어 코드 (71=Python 3.8.1)
    ast_conditions = Column(Text, default="[]")            # JSON 직렬화된 AST 조건
    global_ast_conditions = Column(Text, default="[]")     # JSON 직렬화된 전역 AST 조건
    test_cases = Column(Text, default="[]")                # JSON 내장 [{"stdin": ..., "expected_output": ...}]
