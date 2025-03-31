from fastapi import FastAPI, Header
import uvicorn
from typing import List

from pydantic import json

from schemas.login import LoginResponse, LoginData, TokenData, Token
from schemas.message import Message, SentMessage, PolledMessage

app = FastAPI(debug=True)

@app.get("/")
def read_root():
    return "Hello World!"

@app.post("/login", response_model=List[LoginResponse])
def login(login_data: LoginData):
    response = []
    for bot in login_data.bots:
        token = TokenData(bot=bot)
        response.append(LoginResponse(token=token.encrypt(), bot=bot))

    return response


@app.post("/message", response_model=List[SentMessage])
def send_message(messages: List[Message], token: Token = Header("token")):
    bot = token.decrypt().bot

    results = []

    for message in messages:
        result = bot.send_message(message)
        results.append(result)

    return results


@app.get("/message")
def get_messages(token: Token = Header("token")):
    bot = token.decrypt().bot
    results = bot.poll_messages()

    polled_messages = []

    for message_data in results:
        author_display_name = message_data["author"]["displayName"]

        message_dict = {
            "message_id": message_data["id"],
            "type": message_data["type"],
            "sender_id": message_data["from"],
            "sender_name": author_display_name,
            "text": message_data["text"],
            "timestamp": message_data["timestamp"]
        }

        if "attachments" in message_data and message_data["attachments"]:
            transformed_attachments = []

            for attachment in message_data["attachments"]:
                transformed_attachment = {
                    "attachment_id": attachment["id"],
                    "metadata": attachment["metadata"],
                    "size": attachment["size"],
                    "attachment_name": attachment["name"],
                    "_key": attachment["_key"],
                    "_digest": attachment["_digest"]
                }
                transformed_attachments.append(transformed_attachment)

            message_dict["attachments"] = transformed_attachments

        polled_message = PolledMessage(**message_dict)
        polled_messages.append(polled_message)
    return polled_messages


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)