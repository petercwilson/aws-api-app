# AI App — Render Deployment

A lightweight FastAPI app that wraps the Anthropic API, deployable to Render's free tier in ~3 minutes.

## Deploy to Render

### Option A — One-click (Blueprint)
1. Push this folder to a GitHub repo
2. Go to https://dashboard.render.com → **New** → **Blueprint**
3. Connect your repo — Render reads `render.yaml` automatically
4. When prompted, paste your `ANTHROPIC_API_KEY`
5. Click **Apply** — done

### Option B — Manual
1. Go to https://dashboard.render.com → **New** → **Web Service**
2. Connect your GitHub repo
3. Set:
   - **Runtime**: Python
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
4. Add environment variable: `ANTHROPIC_API_KEY` = your key
5. Click **Create Web Service**

## Test It

```bash
# Health check
curl https://your-app.onrender.com/

# Chat
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, what can you do?"}'
```

## Free Tier Notes

- Render free services **spin down after 15 min of inactivity** — first request after sleep takes ~30s to wake
- 750 hours/month free (enough for one always-on service)
- No credit card required

## Files

| File | Purpose |
|---|---|
| `app.py` | FastAPI app — `/` health check, `POST /chat` endpoint |
| `requirements.txt` | Python dependencies |
| `render.yaml` | Render Blueprint for one-click deploy |
