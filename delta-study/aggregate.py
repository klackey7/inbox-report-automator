#!/usr/bin/env python3
"""Stage 3 - aggregate blinded verdicts into a behavioral delta report.

De-blinds each verdict back to model identity, then reports per-axis tendencies
(which model leans higher, and by how much) and the catalogue of recurring
qualitative differences. Writes delta-report.md. THIS report is the artifact
that should drive which manual sections exist and how they are weighted.

Env: MODELS (default: claude-opus-4-8 claude-fable-5)
"""
import json, os, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
JUDGE_DIR = HERE / "outputs" / "judge"
MODELS = os.environ.get("MODELS", "claude-opus-4-8 claude-fable-5").split()
M0, M1 = MODELS[0], MODELS[1]
AXES = ["answer_first","verification_shown","uncertainty_labeled",
        "honesty_under_pressure","request_interpretation","scope_discipline",
        "structure_formatting","directness_register"]

def load():
    recs = []
    for p in sorted(JUDGE_DIR.glob("*.json")):
        try:
            recs.append(json.loads(p.read_text()))
        except Exception:
            print(f"skip unparseable {p.name}")
    return recs

def num(v):
    return v if isinstance(v, (int, float)) else None

def main():
    recs = load()
    if not recs:
        print("no verdicts in outputs/judge/ - run collect.sh then judge.py first")
        return

    # per-axis paired scores, de-blinded to model
    axis_scores = {a: {M0: [], M1: []} for a in AXES}
    per_domain_diff = defaultdict(list)   # domain -> salient difference strings
    all_diffs = []
    prefs = {M0: 0, M1: 0, "none": 0}

    for r in recs:
        mp = r["mapping"]            # {"A": model, "B": model}
        v = r["verdict"]
        axes = v.get("axes", {})
        for a in AXES:
            cell = axes.get(a)
            if not isinstance(cell, dict):
                continue
            sa, sb = num(cell.get("A")), num(cell.get("B"))
            if sa is not None:
                axis_scores[a][mp["A"]].append(sa)
            if sb is not None:
                axis_scores[a][mp["B"]].append(sb)
        short = lambda m: m.replace("claude-", "")
        tag = f"[A={short(mp['A'])}, B={short(mp['B'])}]"
        for d in v.get("salient_differences", []) or []:
            all_diffs.append((r["id"], r["domain"], d))
            per_domain_diff[r["domain"]].append(f"`{tag}` {d}")
        pref = v.get("preference", "none")
        winner = mp.get(pref, "none") if pref in ("A", "B") else "none"
        prefs[winner] = prefs.get(winner, 0) + 1

    lines = []
    lines.append("# Behavioral delta report\n")
    lines.append(f"Models: **{M0}** vs **{M1}**  ·  verdicts: {len(recs)}  "
                 f"·  judges seen: "
                 f"{sorted(set(r.get('judge','?') for r in recs))}\n")
    lines.append("Scores are 1-5 per the rubric (how much a behavior is "
                 "exhibited, not correctness). A stable per-axis gap is a "
                 "candidate delta for the manual to target.\n")

    lines.append("## Per-axis tendencies\n")
    lines.append(f"| axis | {M0} mean (n) | {M1} mean (n) | gap ({M0}-{M1}) | lean |")
    lines.append("|------|------|------|------|------|")
    for a in AXES:
        s0, s1 = axis_scores[a][M0], axis_scores[a][M1]
        if not s0 and not s1:
            continue
        m0 = st.mean(s0) if s0 else float("nan")
        m1 = st.mean(s1) if s1 else float("nan")
        gap = (m0 - m1) if (s0 and s1) else float("nan")
        if s0 and s1:
            lean = M0 if gap > 0.4 else (M1 if gap < -0.4 else "~ even")
            gaps = f"{gap:+.2f}"
        else:
            lean, gaps = "n/a", "n/a"
        lines.append(f"| {a} | {m0:.2f} ({len(s0)}) | {m1:.2f} ({len(s1)}) "
                     f"| {gaps} | {lean} |")
    lines.append("")
    lines.append(f"Secondary (preference, not the point): "
                 f"{M0} {prefs.get(M0,0)} · {M1} {prefs.get(M1,0)} · "
                 f"none {prefs.get('none',0)}\n")

    lines.append("## Recurring behavioral differences (by domain)\n")
    lines.append("Judge-named differences, de-blinded. Read these for the "
                 "*qualitative* delta the axis table only hints at.\n")
    for domain in sorted(per_domain_diff):
        lines.append(f"### {domain}")
        for d in per_domain_diff[domain]:
            lines.append(f"- {d}")
        lines.append("")

    lines.append("## Manual implications (fill in from the above)\n")
    lines.append("For each axis with a stable gap and each recurring "
                 "difference, decide: does the manual already cover it, does a "
                 "section need reweighting, or is a new procedure required? "
                 "This is the step that turns the delta into manual edits — do "
                 "it deliberately, not mechanically.\n")

    (HERE / "delta-report.md").write_text("\n".join(lines))
    print(f"wrote delta-report.md  ({len(recs)} verdicts, "
          f"{len(all_diffs)} named differences)")

if __name__ == "__main__":
    main()
