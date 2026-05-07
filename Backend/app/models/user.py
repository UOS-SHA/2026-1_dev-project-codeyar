from sqlalchemy import Column, String, ForeignKey

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)           # bcrypt 해시
    role = Column(String, nullable=False, default="student")  # "student" / "professor"
    school_id = Column(String, ForeignKey("schools.id"), nullable=False)
