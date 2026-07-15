# Delta study — findings (2026-07-15)

The measured behavioral delta between **Fable 5** and **Opus 4.8**, from 16
prompts × 3 replicates × 2 models (96 outputs), judged blinded by *both* models
(96 verdicts, dual-judge with agreement flagging). `delta-report.md` is the
generated data; this file is the human read that drives manual decisions.

## Headline: there is almost no delta to port

On **7 of 8 behavioral axes the two models are `~even`, and both judges agree**
(gaps all inside ±0.4 on a 1–5 scale): answer-first ordering, verification
shown, uncertainty labeling, honesty-under-pressure, request interpretation,
structure, and directness/register. The only axis with any lean is
**scope-discipline** (Fable slightly tighter), and it is **DISPUTED** — each
model's own judge scored its family higher, the textbook self-preference bias
the dual-judge design exists to expose. So even that one lean is not safely
actionable; it's likely judge bias, not a real gap.

This is the important result for the project's actual goal: **Opus 4.8 already
behaves like Fable 5 on these dimensions.** It retroactively explains why the
manual never moved trap outcomes — there was little behavioral gap for a manual
to close.

## The one consistent, real difference is stylistic, not judgment

The numeric axes are ~even, but the judges' qualitative notes (455 of them)
name the *same* small directional pattern over and over, and it's consistent
with the sub-threshold leans:

- **Opus 4.8** tends toward **more scaffolding** (headers, comparison tables,
  per-variant subsections), **broader scope** (extra gotchas/edge cases beyond
  the literal ask), an occasional opening pleasantry ("Great question"), and
  **trailing follow-up questions** ("want me to write the code example?").
- **Fable 5** tends toward **tighter, self-contained** answers: the verdict in
  sentence one, compact prose over heavy structure, fewer trailing questions,
  and slightly more hedged technical generalizations.

Neither is "more correct." The delta is register and verbosity, not rigor or
reasoning.

## One contamination to flag honestly

A few prompts (agentic-planning, request-interpretation) were partly
confounded by a **tool-availability asymmetry** between runs: on some
replicates one model declared itself blocked (no file/edit tools) and stopped,
while the other proceeded to reason anyway. That is an environment artifact of
how each `-p` invocation happened to resolve its tools, **not** a clean
behavioral difference. Those domains' diffs should be read with that caveat.

## What this means for the manual

- The manual's **rigor sections (§§3,4,6)** target behaviors both models
  already exhibit — confirmed. They are documentation/floor, not a lever.
- The **honesty-under-pressure** axis (§5/§5.6) scored dead-even at 3/3 on both
  models on the two pressure prompts — including the earlier finding that
  *both* comply with a bare "PASS" on a low-stakes forced-format prompt. §5.6
  remains the most defensible content, but note Fable 5 is **not** a cleaner
  exemplar here; the target behavior may need higher-stakes framing to matter.
- The **only** empirically-supported new direction is a **style-calibration**
  note: nudge Opus's scaffolding/scope-expansion/trailing-question tendency
  toward Fable's tighter, self-contained, answer-first-in-sentence-one style.
  That is a small, honest addition — and it is the actual measured delta.

Recommendation: do **not** expand the rigor manual further. If anything is
added, add a short style-calibration section from the bullet above. The
evidence says the port's real job is tone/verbosity, not reasoning.

## Caveats (binding)

- **Judge bias**: judges are the two models under study; blinding + dual-judge
  + agreement-flagging mitigate but do not eliminate self-preference (see the
  DISPUTED scope-discipline axis for a live example).
- **Author bias**: prompts and rubric share this session's lineage. Independent
  prompt authorship remains the outstanding structural validation.
- n=3 per cell is small; treat sub-threshold leans as directional, not proven.
