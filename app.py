"""
AI App — FastAPI server for Render deployment.
Uses Anthropic API directly (set ANTHROPIC_API_KEY in Render environment variables).
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Anthropic client — reads ANTHROPIC_API_KEY from environment automatically
client = anthropic.Anthropic()

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
MODEL = os.environ.get("MODEL", "claude-haiku-4-5")


class ChatRequest(BaseModel):
    prompt: str

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("prompt cannot be empty")
        if len(v) > 4000:
            raise ValueError("prompt exceeds 4000 character limit")
        return v


@app.get("/")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/chat")
async def chat(req: ChatRequest):
    logger.info("Prompt length: %d", len(req.prompt))
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system="You are a helpful AI assistant. Be concise and accurate.",
            messages=[{"role": "user", "content": req.prompt}],
        )
        return {
            "response": message.content[0].text,
            "model": MODEL,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key — check ANTHROPIC_API_KEY env var")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit hit — retry later")
    except Exception as e:
        logger.error("Error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
