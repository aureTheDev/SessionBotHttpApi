from datetime import datetime
from typing import Optional, List, Dict, ClassVar
from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator, constr, RootModel


class Message(BaseModel):
    recipient_id: constr(min_length=66, max_length=66)
    text: str

    @field_validator('recipient_id', mode='before')
    def id_must_be_exactly_66_chars(cls, v):
        """
        Validate that the recipient_id is exactly 66 characters long.
        """
        if len(v) != 66:
            raise HTTPException(status_code=422, detail="ID must contain exactly 66 characters.")
        return v


class SentMessage(BaseModel):
    message_hash: str
    sync_message_hash: str
    timestamp: datetime

    # Sample data for SentMessage
    sample_data: ClassVar[list] = [
        {
            "messageHash": "EEBKNEQzIXkY8v4CD3HefzkX3IpkcBL1qW0MBwCeAnU",
            "syncMessageHash": "sK3wqzMm8VP1uxIt6qfU1ZOaMccV3WfX6dgHoudKmLI",
            "timestamp": 1743267493077
        },
        {
            "messageHash": "L9R9kXX9z3ggWIJwCXk3OUHKg1LB+Pnp7H31smMzzJ0",
            "syncMessageHash": "V4A/AVc80bXF+enCCsLSFwWKn2uHB3ix0yVHFmw8aFg",
            "timestamp": 1743267493082
        }
    ]


class AttachmentKey(RootModel[List[int]]):
    pass


class AttachmentDigest(RootModel[List[int]]):
    pass


class AttachmentMetadata(BaseModel):
    width: int
    height: int
    content_type: str = Field(..., alias="contentType")


class Attachment(BaseModel):
    attachment_id: str
    metadata: AttachmentMetadata
    size: int
    attachment_name: str
    _key: Dict[str, int]
    _digest: Dict[str, int]


class PolledMessage(BaseModel):
    message_id: str
    type: str
    sender_id: str
    sender_name: str
    text: str
    attachments: Optional[List[Attachment]] = None
    timestamp: datetime