import jwt
import os
from sqlmodel import SQLModel, Session, Field, create_engine
from models import BotTable
import uuid
from datetime import date, datetime


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
        session = Session(engine)

        try:
            row = session.query(BotTable).filter(BotTable.bot_id == self.bot_id).first()
            if not row:
                raise ValueError(f"Bot with ID '{self.bot_id}' not found in DB.")

            self.bot_name = row.bot_name
            self.bot_dob = row.bot_dob
            self.bot_key = row.bot_key
            self.bot_role = row.bot_role

        finally:
            session.close()

        return self


    @classmethod
    def create_bot(cls, creation_data: dict, secret=os.getenv("SECRET_KEY"), engine_url=os.getenv("DATABASE_URL")):

        engine = create_engine(engine_url)
        with Session(engine) as session:
            new_bot_id = str(uuid.uuid4())
            bot_dob = creation_data.get("bot_dob")
            if isinstance(bot_dob, str):
                bot_dob = date.fromisoformat(bot_dob)
            new_bot = BotTable(
                bot_id=new_bot_id,
                bot_name=creation_data.get("bot_name"),
                bot_dob=bot_dob,
                bot_key=creation_data.get("bot_key"),
                bot_role=creation_data.get("bot_role")
            )
            session.add(new_bot)
            session.commit()
            session.refresh(new_bot)

        token_payload = {
            "bot_id": new_bot.bot_id,
            "bot_name": new_bot.bot_name,
            "bot_role": new_bot.bot_role,
            "iat": datetime.utcnow().timestamp()
        }
        token = jwt.encode(token_payload, secret, algorithm="HS256")
        return cls(token, secret)

