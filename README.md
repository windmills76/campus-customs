# Campus Customs

A Yale-branded merch shop built for AI Foundations Homework 4: a React + Vite + TypeScript
storefront backed by a FastAPI API, growing into a Pydantic AI-powered shopping assistant.

## Project layout

```
backend/    FastAPI app (products API, image serving; agent brain comes in a later problem)
frontend/   React + Vite + TypeScript storefront
data/       SQLite database + product images (gitignored, NOT committed — see below)
output/     harness.md — living design/spec notes, started in Problem 2
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

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The frontend expects the backend at `http://localhost:8000` by
default (override with `VITE_API_BASE` in `frontend/.env`, see `frontend/.env.example`).
