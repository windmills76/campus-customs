# Campus Customs

A Yale-branded merch shop built for AI Foundations Homework 4: a React + Vite + TypeScript
storefront backed by a FastAPI API, with a Pydantic AI shopping-assistant agent as its brain.

## Project layout

```
requirements.txt    Backend Python dependencies (installed from the repo root)
.env.example         Copy to .env and fill in your own PORTKEY_API_KEY
AI_prompts.md        Log of prompts used per problem
frontend/            React + Vite + TypeScript storefront
backend/
  main.py            FastAPI app (run with uvicorn) — products, auth, and chat routes
  agent.py           Pydantic AI agent wiring (prompt file + Portkey-hosted model + usage limits)
  tools.py           Tools the agent can call (catalogue search, stock lookup)
  models.py          Shared Pydantic / Pydantic AI types
  prompts/prompt.md  Agent system prompt (Campus Customs voice + safety rules)
  db.py / security.py / safety.py / audit.py   Supporting backend code (DB access, password
                     hashing, sensitive-data redaction, append-only activity log)
output/
  harness.md          Living design/spec doc — how the whole system works
  usability.md        Problem 9 usability improvements write-up
  design.md           Problem 10 visual design write-up
  app_check.html      Problem 11 live app-check report (open directly in a browser)
  app_check_images/   Screenshots linked from app_check.html
  audit_trail.json    Append-only agent activity log (JSON Lines; committed as evidence)
```

Not included in this repo (see Data setup below): `data/campus_customs.db` and `data/products/`.

## Data setup (required — not included in this repo)

The product database and images are intentionally **excluded from git**. Unzip your `data.zip`
into the repo root so it looks like:

```
data/
  campus_customs.db
  products/*.jpg
```

## Backend setup

1. Copy the env template and fill in your own key:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set `PORTKEY_API_KEY` (required for the chat agent; the rest of the site works
   without it). `backend/agent.py` walks up from `backend/` looking for a `.env` file, so a `.env`
   placed here at the repo root is found automatically — no path configuration needed.

2. Install dependencies and run the API (from the repo root):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd backend
   uvicorn main:app --reload --port 8000
   ```

3. Health check: `curl http://localhost:8000/api/health`

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The frontend expects the backend at `http://localhost:8000` by
default (override with `VITE_API_BASE` in `frontend/.env`, see `frontend/.env.example`).
