# Usability Improvements — Campus Customs

Two front-end improvements (look better / easier to use) and two agent/backend improvements
(better, more accurate, or cheaper/faster agent output), picked for this problem.

## Front-end

### 1. Product search & category filter on the Products page
**What was added:** A search box and a garment-type dropdown above the product grid
(`frontend/src/pages/Products.tsx`). Typing filters the grid instantly by name, description, or
search tags; the dropdown narrows to one garment type (hoodie, t-shirt, crewneck, etc.), built
dynamically from whatever's actually in the catalogue. A live "X of 102 products" count and a
"no products match" empty state replace a silently-empty grid.

**Why it helps:** The catalogue has 100+ items and was previously one long scroll with no way to
narrow it down. A shopper who knows they want "something navy" or "just crewnecks" had to scan
everything by eye. This is the single highest-leverage usability fix for a catalogue this size —
less scrolling, faster to the item they actually want, which means fewer shoppers giving up before
finding something to buy.

### 2. Responsive mobile navigation (hamburger menu)
**What was added:** Below ~640px wide, the nav bar's links collapse behind a hamburger toggle
button instead of wrapping awkwardly across multiple lines (`frontend/src/components/NavBar.tsx`,
`App.css`). Tapping it opens a stacked dropdown with the same links; it closes automatically after
a link is tapped.

**Why it helps:** College shoppers browsing merch are disproportionately likely to be on a phone.
The previous nav bar just wrapped (Home / Products / About Us / Hi, Name / Log Out stacking into
two cramped lines), which looks unfinished and makes the brand look less trustworthy on the device
most shoppers will actually use. A clean, tap-friendly nav is a basic trust signal for an online
store.

## Agent / Backend

### 1. In-memory catalogue cache (faster, cheaper agent turns)
**What was added:** `backend/db.py`'s `list_products()` — which does a full catalogue scan plus
one inventory query *per product* (103 SQLite queries for 102 products) — is now cached in memory
for 60 seconds. `search_catalogue`, the agent's main discovery tool, calls `list_products()` on
essentially every category question, so before this change a single chat turn could trigger that
full 103-query scan more than once.

**Why it helps:** Fewer, cheaper round-trips per tool call means lower latency per chat reply (the
shopper waits less) and lower compute cost for Campus Customs to run the assistant at scale — this
is squarely a "make the agent run faster or cheaper" improvement. A 60-second TTL is safe here
because nothing in this app writes to the catalogue or inventory at runtime, so staleness risk is
effectively zero while still bounding it rather than caching forever.

### 2. Budget-aware catalogue search (more accurate answers to "under $X" questions)
**What was added:** `search_catalogue` now accepts optional `max_price`/`min_price` arguments
(`backend/tools.py`), and `backend/prompts/prompt.md` was updated to tell the agent to pass them
whenever a shopper gives a budget, instead of deciding for itself which results "look" affordable.
Filtering happens in code against the real `catalogue.price` column, not in the model's head.

**Why it helps:** Before this, a question like "what's under $35?" with no category word returned
nothing (no keyword to match on), and a question like "hoodies under $70" relied on the model
correctly reading and comparing prices itself across several results — an easy place for an LLM to
make an arithmetic or reading slip, which is exactly the kind of price inaccuracy Campus Customs
can't afford from its "honest stock, honest prices" promise. Now the price boundary is enforced by
the database query, not model reasoning, so a shopper asking about a budget gets a guaranteed-
correct list every time.
