# AI Prompts Log — Campus Customs (HW4)

Per-problem log of the prompts used with Claude Code to build this project. Evidence of each problem's completion is the running site, the database writes, and screenshots — this file only tracks the prompts.

---

## Problem 1 — Vibe Coder Prompts

**Prompt:**
> Problem 1 is called vibe coder prompts. create ai_prompts.md and for each probelm you need to record the problem number and title, at least one prompt used per question and a follow up prompt if needed after the first one. if a prompt requires a follow up, write a sentence about what was lacking from the first prompt. running site, databse writes, and screenshots are the evidence -- you do not need an extra rpoof essay beyond these prompts.

No follow-up needed.

---

## Problem 2 — Analyze the Database

**Prompt:**
> Problem 2 is called analyze the database. look at the database in campus_customs.db. understand the catalogue, inventory, and users. start the file output/harness.md where you write down each table and its fields, and one short line on why each field matters for the sop or the chatbot. We will keep this harness file in later problems with models, tools, safety, specs.

No follow-up needed.

---

## Problem 3 — Build the Campus Customs Website

**Prompt:**
> Problem 3 is called Build the campus customs website. Scaffold a React + Vite + Typescript front end for campus customs. put a nav bar at the top that links to the main pages: home, products, about us, log in, and create account. Pull campus customs-style wording from yalebulldogblue.com for Home and About Us, but write these pages in a different voice and not exactly what's written on the website. On the products page of the website, show product images from the cataloge (use the image paths in the databse)( with basic product information like name price and a short description. Make each product open a single-item page (large image on the left, full product text on the right with description, price, sizes/stock when you have them). clicking a card on products should take the shopper there. Add a chat interface in the bottom right of the site -- a floating chat panel is perfect. It does not need to talk to an agent yet - a stub that will call the backend later is enough for this problem. We will need a small API soon to read the databse and we need to start a simple FastAPI app in backend/main.py just to serve products and images, then grow it into the agent backend in problem 5.

No follow-up needed.

---

## Problem 4 — Create Account and Login

**Prompt:**
> Problem 4 is called create account and login. Build a normal creat-account/login flow. Create account should ask for first name, last name, email, password (confirm password where it makes the user type the same password twice and won't allow submission until they are identical). Log in should be email and password. New account go into the users table. Make sure to store passwords securely so hackers (human or AI) cannot access them by hashing them. The seed database already has a test use you can use while building: email: test@campuscustoms.yale.edu password: password. Confirm you can log in as that user and that a brand new account you create works.

**Follow-up:**
> update output/harness.md with how auth works (what you store for a user and how passwords are protected)

What was lacking from the first prompt: it specified the signup/login behavior but not that the harness file (started in Problem 2) should capture the auth/security design, so a follow-up called that out explicitly.

---

## Problem 5 — Pydantic AI Agent Backend

**Prompt:**
> Problem 5 is called pydantic ai agent backend. Build the shop chatbot as a pydantic ai agent behind fast API, plugged into the front-end chat widget. Put the api app in backend/main.py that is the file you run with uvicorn. keep the agent as these four files next to it: backend/prompts/prompt.md - system prompt to be grown later, backend/agent.py 0 agent entry and wiring, backend/tools.py - tools the agent can call and backend/models.py - pydantic/pydantic ai structured types. in main.py, expose a chat route so a message formt eh wesbite reutnr a reply form the agent and whatever else you need for products/auth. you will need the ai model API key found in the ai foundations folder on this computer. Put campus customs cvoice and safety basics into prompts/prompt.md and we will grow this later. start or update types in models.py for chat replies and product cards as needs. in output/harness.md, note how the front end talks to fastAPI and how the agent is loaded (prompt file + model). make sure the backend runs from the backend/ folder like this: uvicorn main:app --reload --port 8000

No follow-up needed.

---

## Problem 6 — Tools: Product Info and Stock

**Prompt:**
> Problem 67 is called Tools: product info and stock. Give the agent tools that look up real information from campus_customs.db: product description, price, how many are in stock (by size and when the customer asks). The agent must use the database -- it should not invent prices or quantities. If a size is out of stock, say so clearly. Expand prompts/prompt.md so the agent knows to call these tools for price and stock questions. add or update return types in models.py. IN output/harness.md, list each tool and explain which model fields you chose for lookup results and why.

No follow-up needed.

---

## Problem 7 — Chat Search That Updates the Page

**Prompt:**
> Problem 7 is called Chat search that updates the page. Now we will add a neat feature to the site. when a customer asks about a type of item - for example, what kind of hoodies do you have? - the agent should search the cataloge and the website should dynamically show those matching items as product cards (image, name, price short info). This is an API contract: the agent returns the structure product matches and then the front end renders them on the website. After the dynamic product cards are loaded by the new feature, make sure the same single-item page behaviro build in problem 3 still works: each product card - including the ones the chat just put on the page - should still open that detail view (large image + ful info when clicks. Update prompts/prompt.md and output/harness.md so it is clear how search results reach the page.

No follow-up needed — while verifying in the browser, found and fixed a related issue on my own (the dynamic panel burying the detail page below the fold, and a redundant panel showing over the detail page itself), documented in output/harness.md rather than requiring a follow-up prompt.

---

## Problem 8 — Customer Memory

**Prompt:**
> Problem 8 is called Customer memory. When a shopper is logged into their account, save their chat history in the databse in an appropraite table and reload it when they return. the agent should know who is chatting (name and email) put this in agent deps or an reqivalent clear pattern and/or tools the agent can call. Also pass enough page context that if someone is on a product page and asks do you have this in pinnk the agent knows which item they mean -- putting code into the agent context to do this would be an option. Guest can sitll chat, but their history won't be saved. it only needs to be saved for logged-in users. Document in harness.md how user chat history is stored, what customer fields the agent sees, and how page context is passed.

No follow-up needed. (Chat history persistence/reload into `chat_messages` already existed from Problem 5; this problem's actual new work was adding `ShopperContext` agent deps for identity + page context, verified by asking the agent to state the shopper's name/email and by testing "do you have this in pink?" on a specific product's detail page.)
