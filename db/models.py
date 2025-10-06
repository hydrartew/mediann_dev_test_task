from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy import Text

from db.base import Base


class ApplicationTable(Base):
    __tablename__ = 'application'

    id = Column(Integer, primary_key=True)
    user_name = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
