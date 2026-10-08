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

---

## Problem 9 — Usability Improvements

**Prompt:**
> Problem 9 is called usability improvements. Now that the core shop works, improve it. choose and implement: 2 front-end usability improvements, 2 agent/backend usability improvement. Front-end improvements are things that make the site look better and make it easier to use. Agent/backend improvements are things that make the agent output better, more accurate, or safer. There could be new agent tools or things tha tmake the agent run faster or cheaper. Write output/usability.md before or as you build. for each improvement, say what was added and why it helps a campus customers shopper or the campus customs business. Then make sure all improvements actually show up in the running app. Graders will read the write up and look for these features so ensure that they are exactly aligned.

No follow-up needed. Chose: (front-end) product search + garment-type filter on the Products page, and a responsive hamburger mobile nav; (agent/backend) a 60-second in-memory catalogue cache to cut repeated DB scans per chat turn, and budget-aware (`max_price`/`min_price`) catalogue search so price-bounded questions are filtered in code instead of by model arithmetic. All four verified live in the browser/API before considering the problem done, matching output/usability.md exactly.

---

## Problem 10 — Style the Website

**Prompt:**
> Problem 10 is called style the website. Write output/design.md to say what changed and why it should help customers stick around and buy. Keep this concrete and short. I want to use the current general layout but make the letters more of a bubble glass effect that feels futuristic and high end. this will help shoppers feel better about buying because it won't feel as cheap as the current website and that we care about our online presence by making the design feel modern. I want the fonts, color, hierarchy, motion to be seamless, and product presentation to be straightforward and modern. I think the chat box should mirror this.

No follow-up needed. Restyled the existing layout into a dark glassmorphism theme: Space Grotesk/Inter fonts, a gradient-fill animated "bubble glass" heading treatment, frosted-glass cards/nav/forms/chat panel with one shared accent color and transition timing, color-coded in-stock/out-of-stock pills, and a smooth open/close animation on the chat widget. Found and fixed a CSS specificity bug while verifying live (the product-detail price pill's text was unreadable — a generic `.product-detail-info p` color rule was beating the pill's intended dark text color). Verified across desktop and mobile widths; documented in output/design.md.

---

## Problem 11 — Site Testing (App Check)

**Prompt:**
> Problem 11 is called site testing (app check). test the live site and document it in output/app_check.html (a page you can double-click open). Include clear screenshots and short captions for: 1 chat checking the inventory level of an item (honest stock/price from the DB) 2. the dynamic search-result cards appearing after a categroy question (e.g. hoodies) 3 one of the usability featured we added in problem 9. Make the HTML easy to grade: heading for each chec, screenshot, one or two sentences on what the screenshot proves. Put the screenshot image files in output/app_check_images/ and link them from app_check.html with relative paths (for example app_check_images/inventory.png)

No follow-up needed. Ran the live backend+frontend+agent, captured 3 real screenshots (Champion Reverse Weave Crewneck stock/price question with the answer cross-checked against `campus_customs.db`; the "What kind of hoodies do you have?" dynamic product panel; the Problem 9 search/filter bar narrowing 102 products to 3 by typing "saybrook"), saved them to output/app_check_images/, and wrote output/app_check.html with one heading + screenshot + 1-2 sentence caption per check. Verified the HTML actually resolves its relative image paths by serving output/ with a throwaway local static file server and loading the page in the browser.
