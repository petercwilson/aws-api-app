"""
AI App — Flask server for Render deployment.
No pydantic/Rust dependencies. Uses Anthropic API directly.
"""

import os
import logging
from flask import Flask, request, jsonify
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "1024"))
MODEL = os.environ.get("MODEL", "claude-haiku-4-5")


@app.get("/")
def health():
    return jsonify({"status": "ok", "model": MODEL})


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
    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key"}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit hit — retry later"}), 429
    except Exception as e:
        logger.error("Error: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
