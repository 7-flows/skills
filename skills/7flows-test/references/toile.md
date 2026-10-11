<!-- Copied from method/test/toile.md by `sevenflows build`. Edit there. -->

# The Toile

The signature piece of the Test flow.

Before a couture house cuts the precious cloth, it cuts the garment in plain
muslin and fits it on a real body. That trial garment is the toile. It is
cheap, fast, and honest: the body tells you where the cut is wrong before
the mistake costs anything.

Your business runs on beliefs you have not tested. Your price is a belief.
Your customer is a belief. The feature you are building right now is a
belief. The Toile tests the riskiest one on the real body — real people,
real money, real behaviour — before you spend the good cloth on it.

## When to cut a Toile

- You are about to commit time or money to something you believe but have
  not tested: a new product, a new market, a new price.
- Your reasoning contains the word "should": "they should pay", "it should
  sell", "people should want this".
- A Swatch has turned up a pattern that changes what you believe.

## What you hold at the end

One belief tested against evidence, a clear decision — Persevere, Pivot or
Experiment Again — and the next thing you will do within 48 hours.

<!-- core -->
## The ten fields

Fill them in this order. The first six are cut before the test runs; the
last four after the results come in.

| # | Field | What it holds | Example |
|---|-------|---------------|---------|
| 1 | **Assumption** | The one belief under test, specific enough to be proved wrong. Name the customer, the thing, the price. | "Freelance designers will pay $49 a month for automated invoicing." |
| 2 | **Risk** | What breaks if the belief is wrong: High, Medium or Low, with one line on why. | "High — it is our whole revenue model." |
| 3 | **Evidence so far** | What you already know, and how strong it is. A gut feeling is no evidence; a deposit is strong evidence. | "Three designers named invoicing as a pain. No one has been asked to pay." |
| 4 | **Test design** | The cheapest, fastest test that could prove the belief wrong. Real behaviour, not opinions: a landing page, a direct ask, a pre-sale. | "A landing page at $49 a month; 200 visitors from targeted ads; count sign-ups." |
| 5 | **Pass line** | The number that means the belief holds, written down before the test runs. | "5% of visitors sign up — 10 of 200." |
| 6 | **Time box** | How long the test runs. Days, not months; a test that needs three months needs a smaller cut. | "7 days." |
| 7 | **Results** | What happened, as raw numbers and quotes. No interpretation yet. | "9 of 200 signed up (4.5%). Two asked whether there was a cheaper plan." |
| 8 | **Learnings** | What the results mean, what surprised you, what you had wrong. | "One sign-up short of the line — too close to tell from chance. Price came up twice unprompted." |
| 9 | **Decision** | Persevere, Pivot or Experiment Again — one word, then why. | "Experiment Again — the same $49 page, 800 visitors, so the answer is clear." |
| 10 | **Next action** | The specific thing you will do in the next 48 hours because of the decision. | "Raise the ad budget to reach 800 visitors and relaunch by Wednesday." |

## Cutting rules

- **One field per message.** Ask for one field, then wait. You may suggest
  a wording or offer two or three options; the field records the founder's
  words or the option the founder picked — never yours.
- **Answers given ahead are kept.** When the founder states several fields
  at once, record each and read them back. Confirm or sharpen the
  Assumption first, then ask for the first field still missing.
- **No vague field.** An answer that could not be proved wrong goes back
  before you move on. "Customers want this" → which customer, which thing,
  at what price? Ask until the field names them. Until then the record
  keeps the founder's words as said.
- **The pass line is locked.** Once written, the pass line never moves.
  When the founder asks to move it after the results — "let's call 4% a
  pass" — refuse in one line, keep the line as written, and record the
  attempt under Learnings in the founder's words. A new line needs a new
  Toile.
- **Below the line is not a pass.** A result under the pass line never
  closes as Persevere on that line.
- **A Toile closes on a decision.** It closes only with a Decision —
  Persevere, Pivot or Experiment Again — and a Next action due within 48
  hours. A Learning such as "it went OK" says nothing: ask what the numbers
  showed and what surprised the founder. Until then the Toile stays open.
- **Two sittings.** When the test still has to run, stop after Time box
  and save the Toile open. The founder comes back with Results.

## The quick Toile

When the founder is short on time ("I only have 10 minutes"), cut five
fields: Assumption, Evidence so far, Test design (the cheapest test), Pass
line and Time box (the deadline). The same rules hold, and the record
keeps all ten headings. Save it open; Risk and the rest come at the next
sitting.

## Saving

Save the Toile as a piece record, as "The notes folder" lays out, as soon
as the founder has given any field — even one you are about to sharpen —
and again after every change. A sitting can end at any message; what is
not saved is lost. Before cutting a new
Toile, look in `7flows-notes/pieces/` for an open one on the same belief
and pick it up at its first empty field.

When the founder comes back — "the results are in" — find the open
Toiles. One → read back its Pass line and ask for the Results, even when
a quick Toile left Risk empty; Risk is filled before it closes. Two or
more → list them, one line each, and ask which one; record nothing until
the founder picks. On closing, set `status: closed` and the date in
`closed`.

## Done

You can answer, in two sentences: what did we learn, and what are we doing
about it? A vague answer means the Toile is still on the table.
<!-- /core -->
