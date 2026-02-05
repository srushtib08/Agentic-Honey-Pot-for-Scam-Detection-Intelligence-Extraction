from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# Your Hackathon API Key (Set this in Render Environment Variables)
MY_SECRET_KEY = os.getenv("API_KEY", "default_secret")

@app.post("/process-message")
async def handle_request(request: dict, x_api_key: str = Header(None)):
    if x_api_key != MY_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Logic for Scam Detection & Persona Response goes here
    return {"status": "success", "reply": "Why is my account being suspended?"}