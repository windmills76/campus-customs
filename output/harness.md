# Harness — Campus Customs

Living document, started in Problem 2 (Analyze the Database) and extended in later problems (models, tools, safety, specs).

## Problem 2 — Analyze the Database

Schema of `data/campus_customs.db` (not committed to git — see `.gitignore`).

### `catalogue`
One row per product.

| Field | Why it matters for the shop / chatbot |
|---|---|
| `product_id` (TEXT, PK) | Stable key the agent and frontend use to reference a specific item (e.g. in URLs, tool calls, cart/chat state). |
| `name` | What's shown on product cards, the detail page, and what the chatbot should say back to a shopper. |
| `garment_type` | Lets the chatbot and product filters answer "what hoodies do you have" style questions without parsing free text. |
| `description` | The main text the chatbot can quote or summarize when a shopper asks what an item looks like. |
| `colors` (JSON list) | Lets the chatbot honestly answer "do you have this in X color" instead of guessing from the description. |
| `search_tags` (JSON list) | Keyword surface for matching shopper chat queries ("Yale baseball", "bulldog hoodie") to relevant products — this is the main thing a recommendation/search tool should match against. |
| `image_file_path` | Resolves to the product image shown on cards/detail pages and surfaced in chat; must be served without ever committing the actual image files. |
| `price` | The chatbot must quote this exactly — price honesty is a core requirement, so this is read-only ground truth, never guessed or rounded by the agent. |

### `inventory`
One row per (product, size) combination — the source of truth for stock.

| Field | Why it matters for the shop / chatbot |
|---|---|
| `id` (PK) | Row identity only; not user-facing. |
| `product_id` (FK → catalogue.product_id) | Links stock levels back to a specific product. |
| `size` | Needed to answer "do you have this in a Medium" — stock is per-size, not per-product. |
| `quantity` | The chatbot must check this before claiming an item is in stock; a size with `quantity = 0` must be reported as out of stock, never implied as available. |

### `users`
One row per shopper account.

| Field | Why it matters for the shop / chatbot |
|---|---|
| `id` (PK) | Links a user to their own chat history and (later) orders. |
| `name` | Display name; convenience field alongside first/last name. |
| `email` | Login identifier; must be unique and never echoed back by the chatbot in a way that leaks other users' data. |
| `password_hash` | Never the plaintext password — auth must always compare against this hash, and it must never be logged, returned in an API response, or shown to the chatbot/agent. |
| `created_at` | Account audit trail; not shopper-facing. |
| `first_name` / `last_name` | Used for personalized greetings ("Hi Ada") without needing to parse `name`. |

Note: the DB also ships a `chat_messages` table (id, user_id, role, content, products_json, created_at) with a few seeded example rows — useful as a reference for the exact shape the agent's product recommendations should take (`products_json` mirrors the catalogue+inventory fields plus a derived `image_url` and `total_stock`), but it isn't part of Problem 2's required scope.

## Problem 4 — Create Account & Login

### What we store for a user
Signup only ever writes to the existing `users` row shape — no new columns, no separate credentials table:

| Field | Set from |
|---|---|
| `first_name`, `last_name` | Signup form fields, stored as-is |
| `name` | Derived as `"{first_name} {last_name}"` for display/legacy use |
| `email` | Signup form field, lowercased + trimmed before storage so lookups are case-insensitive; the table's `UNIQUE` constraint on `email` is what actually enforces "no duplicate accounts," not application logic |
| `password_hash` | Never the plaintext password — see below |
| `created_at` | Left to the column's own `DEFAULT (datetime('now'))`, not set by the app |

The plaintext password itself is never written anywhere: not to the DB, not to logs, not echoed back in any API response (`PublicUser` only ever exposes `id`, `first_name`, `last_name`, `email`).

### How passwords are protected
`backend/security.py` hashes with **PBKDF2-HMAC-SHA256, 120,000 iterations, a fresh random 16-byte salt per user**, stored as `pbkdf2_sha256$<salt>$<hex digest>`. This format was reverse-engineered to match the seed database's existing `test@campuscustoms.yale.edu` row exactly (same algorithm tag and hash length), so both seeded and newly-created accounts verify through the same `verify_password()` path — one code path, not a legacy-vs-new split.

- **Why hashing, not encryption:** hashing is one-way. Even with full read access to `campus_customs.db`, an attacker (human or AI) recovers hash digests, not passwords — they'd have to brute-force each one individually, and the salt means two users with the same password get different hashes, defeating precomputed/rainbow-table attacks.
- **Why a per-user random salt:** without it, identical passwords would produce identical hashes, which leaks information and makes precomputed attacks cheap. `secrets.token_hex(16)` is cryptographically random, not predictable.
- **Why 120,000 iterations:** makes each guess computationally expensive, slowing down brute-force/offline cracking attempts without materially affecting real login latency.
- **Constant-time comparison:** verification uses `hmac.compare_digest()` rather than `==`, so timing differences can't be used to guess the hash byte-by-byte.

### Endpoints
- `POST /api/auth/signup` — validates first/last name, a plausible email shape, and a minimum 8-character password (`backend/models.py:SignupRequest`); hashes the password and inserts the user; returns 409 if the email is already taken (relying on the DB's unique index) rather than leaking which emails exist via a separate pre-check.
- `POST /api/auth/login` — looks up the user by email, verifies the password against the stored hash, and returns a generic "Invalid email or password" on any failure (wrong email or wrong password look identical to the client, so the API doesn't reveal which accounts exist).

Confirmed working: the seeded `test@campuscustoms.yale.edu` / `password` account logs in successfully, and a brand-new signup (first/last name, email, password+confirm) is both stored correctly (hashed, unique salt) and can immediately log back in.

## Problem 5 — Pydantic AI Agent Backend

### How the front end talks to FastAPI
`frontend/src/components/ChatWidget.tsx` POSTs JSON to `POST /api/chat` on the same FastAPI app
that already serves products (`backend/main.py`, still the file you run with `uvicorn main:app`):

```
{ "message": "<shopper text>", "user_id": <id or null>, "history": [{role, content}, ...] }
→ { "reply": "<assistant text>", "products": [<full Product objects>, ...] }
```

- `history` is the conversation so far (role/content only, no products) built client-side from
  the widget's own message state — the backend uses it to give the agent real multi-turn memory.
- `user_id` is `null` for guests; chat still works but nothing is saved. When a shopper is logged
  in (via the `useAuth` context from Problem 4), their id is sent along and both the user's
  message and the assistant's reply are written to the existing `chat_messages` table
  (`db.save_chat_message`), with `products_json` populated exactly like the seed data's shape.
- On mount (and whenever the logged-in user changes), the widget calls
  `GET /api/chat/history/{user_id}` to restore prior turns — including their attached product
  cards — so a shopper's conversation survives a page reload.
- The reply's `products` array is rendered as small cards (image, name, price) directly under the
  assistant's bubble, each linking to that product's detail page — this is the "matching items
  appear on the page" behavior from the original goal.

### How the agent is loaded
`backend/agent.py` builds the agent once at import time:
1. **Prompt file**: `backend/prompts/prompt.md` is read via `Path.read_text()` and passed as the
   agent's `instructions` — Campus Customs voice plus the non-negotiable safety rules (never guess
   price/stock, say "out of stock" plainly, stay on-topic, don't leak internal details). This file
   is meant to grow in later problems.
2. **Model**: the course's shared `PORTKEY_API_KEY` lives in the course-root `.env`, several
   directories above this homework folder — `agent.py` walks up from `backend/` through parent
   directories at import time and loads whichever `.env` it finds first (same pattern used in the
   course's Lecture 11 examples). An `AsyncOpenAI` client is pointed at Portkey's gateway
   (`PORTKEY_BASE_URL`, default `https://api.portkey.ai/v1`) with `x-portkey-provider: openai`,
   then wrapped in `pydantic_ai.models.openai.OpenAIResponsesModel` via `OpenAIProvider`. The
   model alias (`MODEL_NAME`, default `gpt-6-luna`) is a Portkey-side alias, not a literal OpenAI
   model name, and is overridable by env var.
3. **Tools** (`backend/tools.py`): `search_catalogue` (keyword overlap search over the real
   catalogue), `get_product_details` (exact product lookup), `get_stock` (real inventory, by size
   or overall) — these are the only way the agent is allowed to learn about products, so it can't
   hallucinate price or availability.
4. **Structured output** (`backend/models.py:AgentReply`): the agent itself only returns
   `{message, product_ids}` — a short reply plus the IDs of products it actually looked up this
   turn. `main.py`'s `/api/chat` route hydrates those IDs into full `Product` records from the DB
   before responding, so the client never trusts the model for product data, only for which
   products are relevant.

Confirmed working end-to-end in the browser: asking about a real category (e.g. "navy hoodies",
"Saybrook college gear") returns an honest reply with matching product cards; asking about
something not in the catalogue (e.g. "Yale surfboards") gets a plain "we don't carry that" instead
of an invented answer; asking something off-topic (e.g. "write me a Python scraper") gets
redirected back to shopping; a follow-up using "it" ("do you have it in a small?") correctly
resolves against conversation history and checks real per-size stock.
