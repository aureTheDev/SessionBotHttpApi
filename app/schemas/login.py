import os
from datetime import datetime, timezone
from typing import ClassVar, Any
import jwt
from fastapi import HTTPException
from pydantic import BaseModel, Field, constr, field_validator

from schemas.bot import Bot, BotBasic


class TokenData(BaseModel):
    bot: Bot
    # Automatically set the creation_date to the current UTC datetime
    creation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def encrypt(self) -> "Token":
        """
        Encode the TokenData instance into a JWT token.
        The creation_date is converted to ISO format for JSON compatibility.

        Returns:
            A Token instance containing the JWT.
        """
        # Serialize the model data and convert the creation_date to an ISO string.
        payload: dict[str, Any] = self.model_dump()
        payload["creation_date"] = self.creation_date.isoformat()
        token_str = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm='HS512')
        # If jwt.encode returns bytes, decode to a string; otherwise, use it directly.
        if isinstance(token_str, bytes):
            token_str = token_str.decode('utf-8')
        return Token(token=token_str)


class Token(BaseModel):
    token: constr(min_length=128, max_length=512)

    def decrypt(self) -> TokenData:
        """
        Decode the JWT token and reconstruct the TokenData instance.
        The creation_date is converted from ISO format back to a datetime.

        Raises:
            HTTPException: If the token is invalid or expired.

        Returns:
            A TokenData instance based on the decoded token.
        """
        try:
            decoded = jwt.decode(self.token, os.getenv('SECRET_KEY'), algorithms=['HS512'])
            decoded["creation_date"] = datetime.fromisoformat(decoded["creation_date"])
            return TokenData(**decoded)
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token.") from e


class LoginData(BaseModel):
    password: str
    bots: list[Bot]

    @field_validator("password")
    def validate_password(cls, v):
        """
        Validate that the provided password matches the expected one.
        Raises an HTTPException with a 401 status code if invalid.
        """
        expected_password = os.getenv("LOGIN_PASSWORD")
        if v != expected_password:
            raise HTTPException(status_code=401, detail="Incorrect password")
        return v

    # Sample data for LoginData (annotated as ClassVar so as not to be treated as model field)
    sample_data: ClassVar[dict] = {
        "password": "sample_password",  # Replace with the expected password for testing
        "bots": [
            {
                "name": "SampleBot",
                "id": "A" * 66,  # Dummy ID exactly 66 characters long
                "mnemonic": " ".join(["word"] * 13)  # Exactly 13 words
            }
        ]
    }


class LoginResponse(BaseModel):
    token: Token
    bot: BotBasic

    # Sample data for LoginResponse
    sample_data: ClassVar[dict] = {
        "token": {
            "token": "x" * 130  # Dummy JWT string between 128 and 512 characters
        },
        "bot": {
            "name": "SampleBotBasic",
            "id": "B" * 66  # Dummy ID exactly 66 characters long
        }
    }