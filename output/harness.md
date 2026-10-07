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
