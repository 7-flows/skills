# Close calls

Nine sign-ups against a line of ten feels like a near pass. It is not
anything yet. Two hundred people is a small fitting: run the same page
again and you could see seven or twelve. A result that close to the line
cannot tell you whether the belief holds, and a decision built on it is a
coin toss dressed as evidence.

<!-- core -->
## Close calls

When the Results are a count against the pass line — sign-ups out of
visitors, buyers out of people asked — call the result before Learnings.
Run the close-call script from the skill's folder (`python` where there
is no `python3`):

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
  visitors." That proposal comes first and stands. If the size looks out
  of reach, say so after it and offer a sharper test as a second option;
  the founder chooses between them — you never drop the larger test.

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
