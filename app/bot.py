import jwt
import os
from sqlmodel import Session, create_engine
from models import BotTable
from schemas import CreateBot, CreatedBot
from typing import List
from typing import List

class Bot:
    def __init__(self, token, secret=os.getenv("SECRET_KEY")):
        self.token = token
        self.decoded_token = self.decode_token(secret)
        self.bot_id = None
        self.bot_name = None
        self.bot_dob = None
        self.bot_key = None
        self.bot_role = None

        if not self.decoded_token:
            raise "The bot token is invalid or expired."

        self.bot_id = self.decoded_token.get("bot_id")
        if not self.bot_id:
            raise "The bot ID is missing from the token."

    def decode_token(self, secret):
        try:
            return jwt.decode(self.token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return "Error: The token has expired."
        except jwt.InvalidTokenError:
            return "Error: Invalid token."

    def query_bot_info(self, engine_url=os.getenv("DATABASE_URL")):
        engine = create_engine(engine_url)

        with Session(engine) as session:
            row = session.query(BotTable).filter(BotTable.bot_id == self.bot_id).first()
            if not row:
                raise ValueError(f"Bot not found")

            self.bot_name = row.bot_name
            self.bot_dob = row.bot_dob
            self.bot_key = row.bot_key
            self.bot_role = row.bot_role

        return self

@classmethod
def create_bot(cls, creation_data: List[CreateBot], secret=os.getenv("SECRET_KEY"), engine_url=os.getenv("DATABASE_URL")) -> List[CreatedBot]:
    engine = create_engine(engine_url)
    created_bots = []

    with Session(engine) as session:
        for data in creation_data:
            new_bot = BotTable(
                bot_id=data.bot_id,
                bot_name=data.bot_name,
                bot_key=data.bot_key,
                bot_role=data.bot_role
            )
            session.add(new_bot)
            session.commit()
            session.refresh(new_bot)

            token = jwt.encode({"bot_id": new_bot.bot_id}, secret, algorithm="HS512")

            created_bot = CreatedBot(
                bot_id=new_bot.bot_id,
                bot_name=new_bot.bot_name,
                bot_key=new_bot.bot_key,
                bot_role=new_bot.bot_role,
                bot_token=token
            )
            created_bots.append(created_bot)

    return created_bots
