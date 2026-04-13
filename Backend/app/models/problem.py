from sqlalchemy import Column, String, Integer

from app.db.base import Base

class Problem(Base):
    __tablename__ = "problems"

    id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    time_limit = Column(Integer)
    memory_limit = Column(Integer)
