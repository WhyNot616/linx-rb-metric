# Independent audit request — LINX, a line-adjusted running back skill metric

You are a skeptical, statistically literate reviewer. Your job is to try to break this
work, not to be nice to it. Verify the numbers first, then judge whether the claims are
calibrated — whether the author claims exactly what the evidence supports, and no more.

**Scope note:** this repository covers LINX (running backs) only. The wider project also
contains receiver, quarterback and tight end metrics and a fantasy projection layer; none
of that is here, and no claim in this repository depends on it.

## What is being claimed

```
LINX = 0.45·z(yards after contact / attempt)
     + 0.30·z(broken tackle rate)
     + 0.25·z(line-adjusted yards before contact / attempt)
```

z-scored within season, 100-carry minimum, 2018–2025, 371 player-seasons. The line
adjustment subtracts the back's own team's carry-weighted yards before contact,
**excluding his own carries** (leave-one-out).

The author frames LINX as a **line-adjusted, predictive metric and a supported
hypothesis — not a proven measurement of intrinsic skill.** Is that framing calibrated?

## How to verify (please actually run these)

```
pip install -r requirements.txt
python3 scripts/verify_all.py
python3 scripts/verify_robustness.py
```

Both print `computed=… claimed=…` for every figure. Confirm they match; diffs under 0.01
are rounding. If a number does not reproduce, that is a real finding — report it.

## The claims to check

- **Blind next-season prediction: r = 0.291** (stabilized LINX, n = 67). This is the
  headline. The single-year version scores 0.214 on the identical pairs. The author says
  the improvement is *suggestive rather than significant* because the bootstrap interval
  on the gain crosses zero. Is that the right level of confidence?
- **Within-season r = 0.632 against YPC-above-team** (n = 371). The author flags this as
  **part-whole** — YAC/att and YBC/att appear on both sides — and uses it only as an
  internal consistency check. Is that disclosure adequate, or is the number still doing
  rhetorical work it hasn't earned?
- **Fitted weights do not beat hand-set weights.** Train on 2018–2022, test on 2024–25:
  Ridge-learned 0.213 vs theory 45/30/25 0.214. In-sample the fitted version looked
  better (train r = 0.33) and collapsed out of sample. Is reporting this as evidence
  *for* the theory weights legitimate, or is it post-hoc justification?
- **vs NGS Rushing Yards Over Expected:** predicting next-season YPC-above-team,
  stabilized LINX 0.258 vs RYOE 0.141 (n = 211). An earlier draft said LINX "subsumes"
  RYOE; that wording is **retracted**. Is the narrower current claim supportable?
- **Injury/availability null:** games missed adds +0.002 R² beyond LINX. Does this
  adequately rule out LINX being a proxy for health?

## Specifically probe for

1. **Leakage / look-ahead.** Any path by which test-period information reaches the
   training step? The leave-one-out line baseline is the obvious place to look.
2. **Part-whole circularity** beyond the 0.632 the author already flags. Is any other
   result graded against its own ingredients?
3. **Sample size.** n = 67 on the headline blind test, n = 211 pairs overall, one weak
   leave-one-season-out fold (2024, r = 0.057). Are the confidence claims hedged
   appropriately, or is a small sample carrying too much weight?
4. **Is it really the line?** r(LINX, ESPN Run Block Win Rate) = 0.031 and stability is
   equal for backs who change teams (0.294) versus stay (0.284). Does that settle it, or
   is there a better test the author hasn't run?
5. **Transductive standardization.** z-scoring is done within season across the full
   2018–2025 panel, including test seasons. Standard practice, no target leakage — but
   does it deserve a footnote?
6. **Hardcoded hyperparameters.** The stabilization uses a 3-year window, decay 0.5 and
   shrinkage K = 200. Were these tuned on data that includes the test years?
7. **Overclaiming.** Anywhere the prose says more than the number supports.

## Please return

- A table: `claim → reproduced? (yes/no) → your value`
- Any statistical problems found — leakage, overfitting, circularity, overclaiming — or
  an explicit "none found"
- A verdict: are the headline claims **supported, overstated, or understated**?
- Any wording you would change to make the paper more defensible before publication
