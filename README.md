# Campus Customs

A Yale-branded merch shop built for AI Foundations Homework 4: a React + Vite + TypeScript
storefront backed by a FastAPI API, with a Pydantic AI shopping-assistant agent as its brain.

## Project layout

```
backend/
  main.py           FastAPI app (run with uvicorn) — products, auth, and chat routes
  agent.py          Pydantic AI agent wiring (prompt file + Portkey-hosted model + usage limits)
  tools.py          Tools the agent can call (catalogue search, stock lookup)
  safety.py         Code-level redaction of card/SSN-like numbers before they reach the model/DB
  audit.py          Append-only JSON Lines activity log (output/audit_trail.json)
  prompts/prompt.md Agent system prompt (Campus Customs voice + safety rules)
  models.py         Shared Pydantic / Pydantic AI types
frontend/   React + Vite + TypeScript storefront
data/       SQLite database + product images (gitignored, NOT committed — see below)
output/
  harness.md          Living design/spec doc — how the whole system works, started in Problem 2
  usability.md        Problem 9 usability improvements write-up
  design.md           Problem 10 visual design write-up
  app_check.html      Problem 11 live app-check report with screenshots
  audit_trail.json    Append-only agent activity log (JSON Lines; committed as evidence, keeps growing)
ai_prompts.md   Log of prompts used per problem
```

## Data setup (required, not included in this repo)

The product database and images are intentionally **excluded from git**. Before running the app,
unzip your `data.zip` into this folder so it looks like:

```
data/
  campus_customs.db
  products/*.jpg
```

## Running the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Health check: `curl http://localhost:8000/api/health`

The chat agent needs a `PORTKEY_API_KEY` (and optionally `MODEL_NAME`, `PORTKEY_BASE_URL`) in a
`.env` file. `backend/agent.py` looks for `.env` in `backend/` and walks up parent directories, so
a shared `.env` higher up in a course/workspace folder is picked up automatically — no need to
copy the key into this repo.

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The frontend expects the backend at `http://localhost:8000` by
default (override with `VITE_API_BASE` in `frontend/.env`, see `frontend/.env.example`).
