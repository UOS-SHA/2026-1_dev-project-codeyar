from sqlalchemy import Column, String

from app.db.base import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)       # 학교 이름 (예: "서울과학기술대학교")
    code = Column(String, unique=True, nullable=False)  # 학교 코드 (예: "UOS")
