from sqlalchemy import Column, String

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String)
    password = Column(String)
