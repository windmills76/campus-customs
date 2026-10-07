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

## Problem 6 — Tools: Product Info and Stock

Three tools in `backend/tools.py`, all reading `campus_customs.db` directly (via `db.py`) — none
of them let the agent answer from memory:

### `search_catalogue(query, max_results=6) -> list[Product]`
Keyword-overlap search across a product's name, garment type, description, colors, and search
tags. Returns the full `Product` type (unchanged from Problem 3/5) because its job is discovery —
giving the agent and the chat UI's product cards everything they need (image, price, stock) for a
browsing-style result, not a single confirmed fact. An empty result means the store genuinely
doesn't carry it, which the prompt leans on to avoid "closest match" hallucination.

### `get_product_info(product_id) -> ProductInfoResult` (`models.py`)
```
ProductInfoResult: found: bool, info: ProductInfo | None
ProductInfo: product_id, name, garment_type, description, colors, price, image_url
```
**Field choices:** `ProductInfo` deliberately leaves out `inventory`/`total_stock` and
`search_tags`. Stock is excluded on purpose — this tool answers "what is it / what does it cost,"
and keeping stock out of its payload means the agent can't accidentally answer a stock question
from a product-info call without ever having called `get_stock`. `search_tags` is internal search
metadata the shopper never asked about and would just waste context. `price` is a bare `float`,
not a formatted string, so the agent (and the prompt's "quote it exactly") always gets the raw
number rather than something pre-rounded or pre-formatted that could drift from the DB.

### `get_stock(product_id, size=None) -> StockLookupResult` (`models.py`)
```
StockLookupResult: found, product_id, total_stock, by_size: list[SizeStock],
                    requested_size, requested_size_quantity, requested_size_in_stock
```
**Field choices:** `by_size` (reusing the existing `SizeStock` type from `Product.inventory`) is
*always* populated, even when the shopper asked about one specific size — so the agent can still
mention "we do have it in other sizes" the way a helpful clerk would, without a second tool call.
The `requested_size_*` fields are `None` unless a `size` argument was actually passed, which keeps
"did the shopper ask about a specific size" unambiguous for the agent instead of it having to
infer that from a generic structure. `requested_size_in_stock` is a plain bool computed from
`quantity > 0` server-side (not left for the model to derive from a number), so "0 means out of
stock" can never be misread or rounded up by the agent.

Both lookup tools return a `found: bool` rather than raising or returning `None` directly, so a
bad `product_id` (e.g. one the agent half-remembers from earlier in the conversation) produces a
clean, typed "not found" the agent can act on instead of a tool error.

`backend/prompts/prompt.md` was expanded with a "Your tools, and exactly when to call them"
section naming all three tools explicitly and tying each to the question type that must trigger
it (price/description → `get_product_info`, availability/size → `get_stock`), plus a rule that a
quantity of 0 must be stated plainly. Verified against the live DB: for the Boola Boola T Shirt
($32.00, L=0 in inventory), the agent correctly quoted $32.00, said "out of stock" for a large,
and listed the exact per-size breakdown (XS 12, S 12, M 15, L out of stock, XL 2, XXL 20) when
asked generally — all matching a direct `sqlite3` query against `campus_customs.db`.

## Problem 7 — Chat Search That Updates the Page

### The API contract
Nothing changed in the HTTP contract from Problem 5/6 — this problem is about what the *frontend*
does with the `products` array `POST /api/chat` already returns:

```
agent (search_catalogue → product_ids in AgentReply)
  → main.py hydrates product_ids into full Product records
  → ChatResponse.products: Product[]   (unchanged shape)
  → frontend: ChatWidget receives { reply, products }
```

The contract is: **the agent decides which products are relevant by returning their IDs; the
frontend is responsible for turning that list into visible product cards.** The agent never
renders anything itself — it just says "these are the real matches," and the page does the rest.

### How the results reach the page
`frontend/src/searchResults.tsx` is a small React context (`SearchResultsProvider`/
`useSearchResults`), separate from the auth context, holding just `{ query, matches }` for the
most recent chat search. `App.tsx` wraps the whole app in it, so it's readable from any route —
the chat widget isn't tied to one page, so the result of a search shouldn't be either.

1. `ChatWidget.tsx` already renders small inline product thumbnails in the chat bubble itself
   (unchanged from Problem 5) — that's immediate in-conversation confirmation.
2. Whenever a chat reply includes `products`, `ChatWidget` additionally calls
   `setMatches(userMessage, products)` on the shared context.
3. `components/ProductMatchesPanel.tsx` reads that context and — reusing the exact same
   `.product-grid` / `.product-card` markup as `pages/Products.tsx` — renders full cards (image,
   name, price, short description) in a labeled "From chat: "..."" section mounted in `App.tsx`
   right below the nav bar, above whatever page content is currently routed. Because it's mounted
   above `<Routes>`, it updates live regardless of which page the shopper is on when they chat —
   confirmed by asking "what kind of hoodies do you have?" while on the About page and watching
   the panel appear there immediately.

### Keeping the Problem 3 single-item page working for these cards
The panel's cards are `<Link to={/products/:productId}>`, the identical route and `ProductDetail`
component every other product card in the app already uses (Products grid, chat-bubble
thumbnails) — there is only one detail-page implementation, so there was nothing new to keep in
sync. Two real issues did surface and got fixed while verifying this in the browser:

- The panel stayed mounted above the routed content, so clicking one of its cards navigated
  correctly but left the actual detail view scrolled out of view below the still-visible grid,
  looking like nothing happened. Fixed with a small `ScrollToTop` effect in `App.tsx` that scrolls
  to the top of the page on every route change.
- Even after scrolling, showing a grid of *other* matches above the *one* product the shopper just
  opened was confusing. `ProductMatchesPanel` now hides itself on `/products/:productId` routes
  specifically (checked via `useLocation`), while still showing on every other page.

Verified end-to-end: asking "what crewnecks do you sell?" from the About page populated the page
panel with real crewneck cards (price, description, image); clicking one navigated to
`/products/champion-reverse-weave-crewneck` and rendered the full single-item page (large image,
$58.00, colors, and a per-size stock table correctly showing L/S/XS/XXL as "Out of stock" and M/XL
with real quantities) — no stale panel, no scroll issue.

## Problem 8 — Customer Memory

### How chat history is stored
No new table was needed — the seed database already shipped a `chat_messages` table shaped
exactly for this (`id, user_id, role, content, products_json, created_at`), analyzed back in
Problem 2. `db.save_chat_message()` (added in Problem 5) writes one row per turn: the shopper's
message (`products_json = NULL`) and the assistant's reply (`products_json` = the same `Product`
list returned to the client, so the saved history can re-render the exact cards the shopper saw).
`db.get_chat_history(user_id)` reads them back ordered by `id`.

**The guest/logged-in split happens in `main.py`, not just by "is user_id present":**
`_build_shopper_context()` looks the user up by ID (`db.get_user_by_id`) and only treats them as
logged in if that row actually exists; `/api/chat` then only calls `save_chat_message` when
`deps.is_guest` is `False`. A guest (`user_id: null`) or a bad/stale ID both get a normal chat
reply with nothing written to `chat_messages` — verified by sending a guest message and confirming
no new row appeared (`SELECT COUNT(*) FROM chat_messages` unchanged) while a logged-in exchange
immediately added two rows. On reload, `ChatWidget` calls `GET /api/chat/history/{user_id}` on
mount (Problem 5) — confirmed in-browser that a full page reload while logged in restores the
entire prior conversation, including product cards, exactly as before the reload.

### What customer fields the agent sees — agent deps, not a tool
`backend/agent.py` defines `ShopperContext` (a plain dataclass: `is_guest`, `name`, `email`,
`current_product_id`) and wires it in as the agent's `deps_type`. `main.py` builds one fresh
`ShopperContext` per request from the real `users` row (never from client-supplied name/email —
the client only ever sends a `user_id`, so a shopper can't claim to be someone else by editing the
request body) and passes it to `shop_agent.run(..., deps=...)`.

The agent is told who it's talking to via a **dynamic instructions function**
(`@shop_agent.instructions`) rather than a tool: it reads `ctx.deps` and injects either "The
shopper is logged in as {name} ({email})" or "The shopper is browsing as a guest — don't address
them by name" into the instructions on every run. This was chosen over a callable tool because the
identity is already known with certainty before the agent does anything — there's no lookup for it
to perform, so forcing a tool call would just add a round-trip for information it should already
have. Verified: asking "what is my name and email, according to you?" as user 1 returns "Test
User, test@campuscustoms.yale.edu"; the same question with `user_id: null` returns "I don't have
access to your name or email... you're browsing as a guest."

### How page context is passed
`frontend/src/components/ChatWidget.tsx` reads the current route with `useLocation()` and, right
before sending a message, checks whether the shopper is on a single product's page
(`/products/:productId`). If so, it sends `page_context: { product_id: "<that id>" }` alongside
the usual `message`/`history`/`user_id` in the `POST /api/chat` body (new `PageContext` model in
`models.py`). `main.py` folds that straight into the same `ShopperContext.current_product_id`
field used for identity — same dependency-injection pattern, not a separate mechanism.

The same `@shop_agent.instructions` function appends a second line when `current_product_id` is
set: it names the exact `product_id` the shopper is looking at and tells the agent to treat an
unqualified "this"/"it" as referring to that product, while still confirming details with
`get_product_info`/`get_stock` rather than trusting the page context's identity alone for price or
stock facts. Verified live: on `/products/champion-reverse-weave-crewneck`, asking "do you have
this in pink?" correctly resolved to that exact crewneck and answered "No — this Champion Reverse
Weave Crewneck comes in light gray and navy blue, not pink" (matching its real `colors` field),
with no product named in the question at all.
