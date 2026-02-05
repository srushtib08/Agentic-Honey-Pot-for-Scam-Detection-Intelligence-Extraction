import re
import requests
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Configuration
MY_API_KEY = "YOUR_SECRET_API_KEY"
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Intelligence Storage (In-memory for hackathon; use Redis/DB for production)
session_intel = {}

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class ScamRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: list[Message] = []
    metadata: dict = {}

def extract_intelligence(text):
    """Regex-based intelligence extraction for Indian scam contexts."""
    return {
        "upiIds": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "phishingLinks": re.findall(r'https?://\S+', text),
        "phoneNumbers": re.findall(r'\b(?:\+91|91)?[6789]\d{9}\b', text),
        "bankAccounts": re.findall(r'\b\d{9,18}\b', text),
        "suspiciousKeywords": [word for word in ["urgent", "verify", "blocked", "suspension"] if word in text.lower()]
    }

@app.post("/process-message")
async def process_scam(request: ScamRequest, x_api_key: str = Header(None)):
    if x_api_key != MY_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 1. Extract and Store Intel
    new_intel = extract_intelligence(request.message.text)
    sid = request.sessionId
    if sid not in session_intel:
        session_intel[sid] = {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "suspiciousKeywords": []}
    
    for key in new_intel:
        session_intel[sid][key] = list(set(session_intel[sid][key] + new_intel[key]))

    # 2. LLM Engagement Logic (The Persona)
    # Hint: Replace this with your actual LLM call (OpenAI/Gemini/Claude)
    ai_reply = "Oh dear, my account is blocked? I use that for my pension. I'm clicking the link but my screen is just white. Can you tell me what to do, beta?"

    # 3. Check for Termination (e.g., if we've gathered enough info or scammer is repeating)
    if len(session_intel[sid]["upiIds"]) > 0 or len(request.conversationHistory) > 10:
        # Trigger the mandatory callback
        callback_payload = {
            "sessionId": sid,
            "scamDetected": True,
            "totalMessagesExchanged": len(request.conversationHistory) + 1,
            "extractedIntelligence": session_intel[sid],
            "agentNotes": "Agent successfully extracted UPI/Phishing data while maintaining a worried elderly persona."
        }
        requests.post(GUVI_CALLBACK_URL, json=callback_payload)

    return {"status": "success", "reply": ai_reply}