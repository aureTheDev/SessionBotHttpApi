from pydantic import BaseModel
from typing import Optional

class BotBase(BaseModel):
    bot_id: str

class CreateBot(BotBase):
    bot_name: str
    bot_mnemonic: str
    bot_role: Optional[str] = None

class CreatedBot(BotBase):
    bot_token: str