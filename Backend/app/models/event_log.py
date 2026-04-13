from sqlalchemy import Column, String

from app.db.base import Base

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    event_type = Column(String)
    detail = Column(String)
