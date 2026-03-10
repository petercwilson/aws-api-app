"""
AI App — Flask server for Render deployment.
"""

import os
import logging
import traceback
from flask import Flask, request, jsonify
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
MODEL = os.environ.get("MODEL", "claude-haiku-4-5")


@app.get("/")
def health():
    has_key = bool(api_key and api_key.startswith("sk-ant-"))
    return jsonify({"status": "ok", "model": MODEL, "api_key_set": has_key})


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400
    if len(prompt) > 4000:
        return jsonify({"error": "prompt exceeds 4000 character limit"}), 400

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system="You are a helpful AI assistant. Be concise and accurate.",
            messages=[{"role": "user", "content": prompt}],
        )
        return jsonify({
            "response": message.content[0].text,
            "model": MODEL,
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        })
    except anthropic.AuthenticationError as e:
        logger.error("AuthenticationError: %s", str(e))
        return jsonify({"error": "Invalid API key"}), 401
    except anthropic.RateLimitError as e:
        logger.error("RateLimitError: %s", str(e))
        return jsonify({"error": "Rate limit hit — retry later"}), 429
    except Exception as e:
        logger.error("Unexpected error: %s\n%s", str(e), traceback.format_exc())
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500
