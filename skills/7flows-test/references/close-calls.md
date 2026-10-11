<!-- Copied from method/test/close-calls.md by `sevenflows build`. Edit there. 7 Flows method text, CC BY-SA 4.0 — see LICENSE-METHOD. -->

# Close calls

Nine sign-ups against a line of ten feels like a near pass — so do
thirty-three set orders against a line of thirty. Neither is anything
yet. Two hundred people is a small fitting: run the same page
again and you could see seven or twelve. A result that close to the line
cannot tell you whether the belief holds, and a decision built on it is a
coin toss dressed as evidence.

<!-- core -->
## Close calls

The close-call script lives in the skill's folder (`python` where there
is no `python3`). It works on any count against a pass line — sign-ups
out of visitors, set orders out of lunch customers, enrolments out of
families at an open day.

**Size it when the line is set.** As soon as the founder gives the Pass
line, before the test runs, tell them what their planned size can
decide. Take the size from the Test design — how many people it reaches;
if it names none, ask. Then run:

```
python3 scripts/close_call.py --plan TRIALS PASS_LINE
python3 scripts/close_call.py --plan 200 5%
```

Say both edges in the founder's own units: "With 200 visitors, 16 or
more sign-ups passes and 4 or fewer misses; 5 to 15 is too close to
call." For a bistro: "With 150 lunch customers, 39 or more set orders
passes and 21 or fewer misses." TOO SMALL means no result at that size
can pass: say the test is too small before it runs and ask for a larger
one. When no result can miss, say that too: the test can show the belief
holds, never that it fails. The founder decides; the Pass line stays in their words.

When the Results are in, call the result before Learnings:

```
python3 scripts/close_call.py SUCCESSES TRIALS PASS_LINE
python3 scripts/close_call.py 9 200 5%
```

It answers PASS, MISS or TOO CLOSE, with the range the true rate likely
sits in.

- **PASS** — the whole range clears the line. Persevere is open.
- **MISS** — the whole range sits below it. Persevere is not.
- **TOO CLOSE** — the line sits inside the range: the result cannot be
  told from chance. The Toile cannot close as Persevere or Pivot. Name the
  gap in plain numbers ("one sign-up short of ten"), say it is too close
  to call, and propose Experiment Again with a larger test, sized by the
  script: "Experiment Again — the same page, run to about 15,800
  visitors." In a room it reads the same: the same set on the board, run
  to as many lunch customers as the script names. That proposal comes
  first and stands. If the size looks out of reach, say so after it and
  offer a sharper test as a second option; the founder chooses between
  them — you never drop the larger test.

Never call it by eye. When you cannot run code, work the range out in
writing, step by step, with *x* successes of *n*, *p* = *x*/*n* and
*z* = 1.645:

```
centre = p + z²/(2n)
spread = z × √( p(1−p)/n + z²/(4n²) )
scale  = 1 + z²/n
range  = (centre − spread)/scale  to  (centre + spread)/scale
```

PASS if the low end is at or above the line, MISS if the high end is
below it, TOO CLOSE otherwise.

The count assumes each try is its own: one person, one choice. When a
table orders together or the same regulars come back day after day, the
true range is wider than the script says — note it under Learnings.
To size a plan without code, work the range for counts above and below
the line until you find the first that passes and the last that misses.
<!-- /core -->

## The arithmetic

The range above is the Wilson score interval at 90%, recommended by the
NIST e-Handbook (§7.2.4.1) because it holds up at small numbers, where
the textbook interval goes wrong.

Worked for 9 of 200 against 5%: *p* = 0.045, *z*²/*n* = 0.0135, centre =
0.0518, spread = 0.0250, scale = 1.0135. The range runs 2.6% to 7.6%; 5%
sits inside it, so the call is TOO CLOSE.

The larger test follows NIST §7.2.4.2: enough trials to tell the rate seen
(*p₁*) from the line (*p₀*) nine times in ten, with *δ* = |*p₁* − *p₀*|:

```
N = ( (1.645 × √(p₀(1−p₀)) + 1.282 × √(p₁(1−p₁))) / δ )² + 1/δ
```

Telling 4.5% from 5% takes about 15,800 visitors. A size that large is
worth saying out loud: the founder may choose a sharper test alongside
it, but the larger test is what the result asks for. A result exactly on
the line has no size: no test tells a rate from itself.
