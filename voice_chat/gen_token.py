# gen_token.py
from livekit import api
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")

token = (
    api.AccessToken(api_key, api_secret)
    .with_identity("dante")
    .with_grants(api.VideoGrants(room_join=True, room="voz"))
    .to_jwt()
)

print(token)
