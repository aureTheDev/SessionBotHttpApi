from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class BotTable(SQLModel, table=True):
    bot_id: str = Field(primary_key=True, max_length=255)
    bot_name: str = Field(nullable=False, max_length=50)
    bot_dob: date = Field(nullable=False)
    bot_key: str = Field(nullable=False, unique=True, max_length=255)
    bot_role: Optional[str] = Field(default=None, max_length=255)