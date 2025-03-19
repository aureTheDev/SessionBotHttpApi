import os
from fastapi import FastAPI, Header
from bot import Bot
import uvicorn
import subprocess
from schemas import CreateBot, CreatedBot
from typing import List



app = FastAPI(debug=True)

@app.get("/")
def read_root():

    base_dir = os.path.dirname(__file__)
    ts_file = os.path.join(base_dir, "session-messenger-utils", "send_message.ts")

    dest = '05e670bba1fc987983b1871fee2dc5a60d27c37152e3054cd73b54a9c2f8b9bf09'

    commande = ["bun", "run", ts_file, dest]

    try:
        résultat = subprocess.run(commande, capture_output=True, text=True, check=True)
        return ("Sortie :", résultat.stdout)
    except subprocess.CalledProcessError as err:
        return (err.stderr)


@app.get("/get_messages")
def get_messages(token: str = Header(..., convert_underscores=False)):
    pass


@app.post("/create_bot")
def create_bot(create_bots: List[CreateBot], response_model=List[CreatedBot]):
    created_bots = Bot.create_bot(create_bots)
    return created_bots

@app.get("/send_message")
def send_message(token: str = Header(..., convert_underscores=False)):
    pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)