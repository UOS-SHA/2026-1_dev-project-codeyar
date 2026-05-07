from sqlalchemy import Column, String, DateTime, ForeignKey

from app.db.base import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)               # 시험명 (예: "알고리즘 중간고사")
    school_id = Column(String, ForeignKey("schools.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)  # 시험 생성 교수
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
