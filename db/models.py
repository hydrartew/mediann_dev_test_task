from sqlalchemy import Column, Identity, Integer, DateTime, String, func
from sqlalchemy import Text

from db.base import Base


class ApplicationTable(Base):
    __tablename__ = 'application'

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    user_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
