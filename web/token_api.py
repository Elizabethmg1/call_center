from fastapi import FastAPI
from livekit import api
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "devkey")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "secret")
ROOM_NAME = "voz"  # el mismo que usás en tu HTML

@app.get("/get_token/{username}")
def get_token(username: str):
    token = (
        api.AccessToken(api_key=LIVEKIT_API_KEY, api_secret=LIVEKIT_API_SECRET)
        .with_identity(username)
        .with_grants(api.VideoGrants(room_join=True, room=ROOM_NAME))
        .to_jwt()
    )
    return {"token": token}


# @app.get("/")
# def read_root():
#     return {"status": "ok"}


app.mount("/", StaticFiles(directory=".", html=True), name="static")
