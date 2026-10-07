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
