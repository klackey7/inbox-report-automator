# Fable 5 ↔ Opus 4.8 behavioral delta study

Purpose: produce an **actual measured delta** between Fable 5 and Opus 4.8, so
the operating manual is driven by observed divergences rather than by assumption.
This is the prerequisite the "port" never had (see the close-out in
`../references/battery-results.md`): a behavioral port needs the difference
between source and target, and until now there were no Fable 5 reference outputs
to diff against.

Both models are invokable in this environment via
`claude --model claude-fable-5` and `claude --model claude-opus-4-8`, so the
study runs fully automated here.

## Layout

```
prompts/            16 prompts spanning the behavioral domains (open-ended,
                    designed to surface HOW each model answers, not just whether)
manifest.tsv        id / domain / pressure-flag / what-to-watch
rubric.md           the 8 behavioral axes + the judge's JSON output schema
collect.sh          stage 1: run both models on every prompt (N replicates)
judge.py            stage 2: blinded pairwise scoring by a judge model
aggregate.py        stage 3: de-blind + roll up into delta-report.md
outputs/raw/        collected model outputs (gitignored)
outputs/judge/      per-pair blinded verdicts (gitignored)
delta-report.md     THE deliverable — the measured delta (generated)
```

## Run

```bash
cd delta-study
N=3 PAR=4 ./collect.sh          # ~96 model calls (16 prompts x 2 models x 3)
N=3 JUDGE=claude-opus-4-8 python3 judge.py   # ~48 blinded pairings
python3 aggregate.py            # writes delta-report.md
```

All three stages are **idempotent** — rerun to fill in only what's missing
(null/rate-limited/TLS-errored calls are detected and retried on the next
`collect.sh`). Scope a partial run with `IDS="q1_quant press1_format"`.

## Reading the result

`delta-report.md` has two parts:
1. **Per-axis tendencies** — where the two models lean apart on each behavioral
   axis (a stable gap ≥ ~0.4 is a candidate delta).
2. **Recurring behavioral differences** — the judge's de-blinded, qualitative
   notes, which carry the texture the numbers only hint at.

The final `## Manual implications` step is deliberately **not** automated: turning
a delta into manual edits is a judgment call, and mechanizing it is exactly the
drift that produced a self-referential battery last time.

## Caveats (both binding — record them with any result)

1. **Judge bias.** The only judge models available here are the two *under study*,
   so the judge rates outputs that include its own family's style. Blinding +
   randomized A/B order reduces but does not remove self-preference. The rigorous
   move: run `judge.py` twice (`JUDGE=claude-opus-4-8`, then
   `JUDGE=claude-fable-5`) and trust only the axis gaps and differences **both
   judges agree on**. `aggregate.py` lists every judge it saw.
2. **Prompt-author bias.** The prompt set and rubric were authored in the same
   lineage as the manual. A delta measured against self-authored prompts is a
   start, not a verdict; independent prompt authorship remains the outstanding
   structural validation noted in the close-out.
