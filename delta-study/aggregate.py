#!/usr/bin/env python3
"""Stage 3 - aggregate blinded verdicts into a behavioral delta report.

De-blinds each verdict back to model identity and reports, PER JUDGE, where the
two models lean apart on each axis. When two judges are present (the recommended
bias control), it flags each axis AGREE (both judges lean the same way) or
DISPUTED. Trust the AGREE axes. Writes delta-report.md - the artifact that
should drive which manual sections exist and how they are weighted.

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
THRESH = 0.4   # |gap| above this = a lean; below = ~even
short = lambda m: m.replace("claude-", "")

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

def lean_of(gap):
    if gap is None:
        return "n/a"
    if gap > THRESH:  return short(M0)
    if gap < -THRESH: return short(M1)
    return "~even"

def main():
    recs = load()
    if not recs:
        print("no verdicts in outputs/judge/ - run collect.sh then judge.py first")
        return
    judges = sorted(set(r.get("judge", "?") for r in recs))

    # axis_scores[judge][axis][model] = [scores]
    axis_scores = {j: {a: {M0: [], M1: []} for a in AXES} for j in judges}
    per_domain_diff = defaultdict(list)
    for r in recs:
        j = r.get("judge", "?"); mp = r["mapping"]; v = r["verdict"]
        for a in AXES:
            cell = v.get("axes", {}).get(a)
            if not isinstance(cell, dict):
                continue
            sa, sb = num(cell.get("A")), num(cell.get("B"))
            if sa is not None: axis_scores[j][a][mp["A"]].append(sa)
            if sb is not None: axis_scores[j][a][mp["B"]].append(sb)
        tag = f"[{short(mp['A'])} vs {short(mp['B'])} as A/B; judge {short(j)}]"
        for d in v.get("salient_differences", []) or []:
            per_domain_diff[r["domain"]].append(f"`{tag}` {d}")

    def gap(j, a):
        s0, s1 = axis_scores[j][a][M0], axis_scores[j][a][M1]
        if not s0 or not s1:
            return None, s0, s1
        return st.mean(s0) - st.mean(s1), s0, s1

    L = []
    L.append("# Behavioral delta report\n")
    L.append(f"Models: **{short(M0)}** (M0) vs **{short(M1)}** (M1)  ·  "
             f"verdicts: {len(recs)}  ·  judges: {[short(j) for j in judges]}\n")
    L.append("Axis scores are 1-5 (how much a behavior is exhibited, not "
             "correctness). Gap = M0_mean - M1_mean; a lean needs |gap| > "
             f"{THRESH}. **Trust axes marked AGREE** across judges.\n")

    L.append("## Per-axis leans" + (" and cross-judge agreement" if len(judges) > 1 else "") + "\n")
    header = "| axis | " + " | ".join(f"{short(j)}: gap (lean)" for j in judges)
    if len(judges) > 1:
        header += " | agreement"
    L.append(header + " |")
    L.append("|" + "---|" * (len(judges) + 1 + (1 if len(judges) > 1 else 0)))
    for a in AXES:
        cells, leans = [], []
        for j in judges:
            g, s0, s1 = gap(j, a)
            if g is None:
                cells.append("n/a (0)"); leans.append(None)
            else:
                cells.append(f"{g:+.2f} ({lean_of(g)}, n={min(len(s0),len(s1))})")
                leans.append(lean_of(g))
        row = f"| {a} | " + " | ".join(cells)
        if len(judges) > 1:
            valid = [x for x in leans if x is not None]
            agree = "AGREE" if valid and len(set(valid)) == 1 else "DISPUTED"
            if not valid:
                agree = "n/a"
            row += f" | **{agree}**"
        L.append(row + " |")
    L.append("")
    if len(judges) > 1:
        L.append("AGREE = both judges lean the same way (incl. both ~even). "
                 "DISPUTED = judges disagree, likely judge bias — do not act on "
                 "these without more data.\n")
    else:
        L.append("_Single judge only — judge-bias uncontrolled. Run judge.py "
                 "with the other model as JUDGE and re-aggregate to get an "
                 "agreement column (see README)._\n")

    L.append("## Recurring behavioral differences (by domain)\n")
    L.append("Judge-named, de-blinded (tag shows the A/B model mapping and which "
             "judge said it). This is the qualitative delta the numbers only hint at.\n")
    for domain in sorted(per_domain_diff):
        L.append(f"### {domain}")
        for d in per_domain_diff[domain]:
            L.append(f"- {d}")
        L.append("")

    L.append("## Manual implications (fill in deliberately)\n")
    L.append("For each **AGREE** axis with a real gap, and each recurring "
             "difference, decide: already covered by the manual, needs "
             "reweighting, or needs a new procedure. Ignore DISPUTED axes until "
             "corroborated. This is the human step that turns the delta into "
             "manual edits — the one place we do NOT mechanize.\n")

    (HERE / "delta-report.md").write_text("\n".join(L))
    ndiff = sum(len(v) for v in per_domain_diff.values())
    print(f"wrote delta-report.md  ({len(recs)} verdicts, {len(judges)} judge(s), "
          f"{ndiff} named differences)")

if __name__ == "__main__":
    main()
