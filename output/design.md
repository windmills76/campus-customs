# Design Refresh — Campus Customs

Problem 10: restyle the existing layout (same pages, same structure) into a modern, "glass"
aesthetic. Kept short and concrete — each change maps to a specific file.

## Typography
Swapped the system sans-serif for **Space Grotesk** (headings, nav, buttons — geometric,
confident) and **Inter** (body copy — clean and highly legible), loaded in `index.html`.
**Why:** the old default system font reads as a placeholder, not a brand. A deliberate
display/body pairing is one of the cheapest signals of a site that was actually designed, not
thrown together — and shoppers price-anchor quality off polish before they read a word.

## Color & glass surfaces
Replaced the flat light-gray background with a deep navy-to-black gradient (`index.css`), and
every card/panel/nav/form (`.product-card`, `.highlight-card`, `.navbar`, `.auth-form`,
`.chat-panel`, etc.) is now a frosted-glass surface: translucent white fill, `backdrop-filter:
blur`, a hairline light border, soft shadow. A single bright azure accent (`--accent`) replaces
scattered blues for buttons, focus states, and highlights.
**Why:** glass-on-dark is the current visual shorthand for "premium tech product" (control
centers, Vision Pro, high-end SaaS). It makes the shop feel built for 2026, not 2010, which
directly addresses "it won't feel as cheap" — perceived quality is one of the strongest levers on
whether someone trusts a site enough to type in a password or a size and actually buy.

## Bubble-glass headings
The site name in the nav and every page's main heading use a gradient text fill (white → pale
cyan → electric blue) with a soft specular drop-shadow and a slow light sweep across the letters
(`.glass-heading` in `App.css`), respecting `prefers-reduced-motion`.
**Why:** this is the literal "bubble glass lettering" ask — glossy, dimensional type reads as
high-end the instant the page loads, before a shopper has scrolled to a single product.

## Motion
One shared transition timing (`220ms cubic-bezier` ease) applied to every hover/focus state —
cards lift and glow, buttons glow, nav links underline smoothly. Page content fades in on route
change, and the chat panel now animates open/closed (scale + fade) instead of snapping in and out.
**Why:** consistent, non-jarring motion is what "seamless" means in practice — it's a continuous
feel from nav to cards to chat, not individually stock standard widgets.

## Product presentation
Product cards and the single-item detail page keep the same information, laid out more plainly:
the image bleeds to the card's edges, price is a small chip instead of plain bold text, and the
size/stock table is now color-coded pills ("In stock · 12" in green, "Out of stock" in muted red)
instead of a number-or-text column.
**Why:** a shopper should be able to tell stock status at a glance, not read a table — faster
scanning means less friction between "interested" and "in stock, in my size, done."

## Chat widget
The toggle button and panel now use the same glass system and accent color as the rest of the
site, with the same open/close motion.
**Why:** the chat widget was the one piece of UI that still looked like a generic support widget
bolted onto the site — it should look like it belongs to Campus Customs, since it's the thing
actually answering "is this real" questions a shopper has before buying.
