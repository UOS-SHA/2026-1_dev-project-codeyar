from sqlalchemy import Column, String

from app.db.base import Base

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    problem_id = Column(String)
    code = Column(String)
    status = Column(String)
