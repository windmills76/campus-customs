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
