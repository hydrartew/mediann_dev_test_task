from datetime import datetime
from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    user_name: str = Field(..., description="Имя пользователя")
    description: str = Field(..., description="Описание заявки")


class Application(BaseModel):
    id: int
    user_name: str
    description: str
    created_at: datetime
