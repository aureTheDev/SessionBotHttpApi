from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, text
from sqlmodel import Field, SQLModel


class BotTable(SQLModel, table=True):
    __tablename__ = "bot"

    bot_id: str = Field(
        default=None,
        primary_key=True,
    )
    bot_name: str = Field(
        ...,
        max_length=50,
        sa_column=Column(String(50), nullable=False)
    )
    bot_dob: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP")
        )
    )
    bot_key: str = Field(
        ...,
        sa_column=Column(String(255), nullable=False, unique=True)
    )
    bot_role: str = Field(
        default=None,
        sa_column=Column(String(255), nullable=True)
    )
