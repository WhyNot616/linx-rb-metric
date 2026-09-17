# LINX — a line-adjusted running back skill metric

Reproduction repository for the LINX metric. Everything claimed in the paper can be
recomputed from this repository with one command, on public data, in under a minute.

```bash
pip install -r requirements.txt
python3 scripts/verify_all.py          # the headline results
python3 scripts/verify_robustness.py   # leakage, line-independence, LOSO, weight sensitivity
```

Both scripts print each value as `computed=… claimed=…` so a reader can confirm or
refute every number without trusting the text.

---

## What LINX is

A per-carry skill score for NFL running backs that adjusts for the quality of the
blocking in front of them:

```
LINX = 0.45·z(yards after contact / attempt)
     + 0.30·z(broken tackle rate)
     + 0.25·z(line-adjusted yards before contact / attempt)
```

z-scored within season, 100-carry minimum, 2018–2025 (371 player-seasons). The
line adjustment subtracts each back's own team's carry-weighted yards before contact,
computed **excluding that back's own carries** (leave-one-out), so a runner is not
compared against a baseline he helped set.

## What the evidence supports, and what it does not

| Result | Value | n | Reading |
|---|---|---|---|
| Blind next-season prediction (stabilized) | **r = 0.291** | 67 | **The headline.** Lead with this. |
| Single-year version, same blind test | r = 0.214 | 67 | Stabilization gain's CI crosses zero — "suggestive," not significant |
| Within-season vs YPC-above-team | r = 0.632 | 371 | **Part-whole.** Shares inputs with the target. An internal consistency check, *not* prediction |
| Year-over-year stability | r = 0.316 | 211 | |
| Fitted weights vs hand-set 45/30/25 | 0.213 vs 0.214 | 67 | Ridge-learned weights **do not beat** the theory weights out of sample |
| vs NGS Rushing Yards Over Expected | LINX 0.258, RYOE 0.141 | 211 | LINX out-predicts RYOE; RYOE adds nothing on top of LINX |
| Games missed, beyond LINX | +0.002 R² | — | Null. LINX is not covertly measuring health |

**The framing we stand behind:** LINX is a *line-adjusted, predictive metric and a
supported hypothesis* — not a proven measurement of intrinsic skill. Running back
year-to-year prediction has a low ceiling for everyone; r ≈ 0.29 is modest and we say so.

**What we deliberately do not claim.** That 0.632 is predictive (it isn't — same season,
shared inputs). That the stabilization gain is statistically significant (its interval
crosses zero). That LINX "subsumes" RYOE (an earlier draft said this; it is retracted —
the defensible claim is the narrower one in the table). That r = 0.29 is impressive.

## Robustness checks (`verify_robustness.py`)

Run after a reviewer argued LINX might be measuring the offensive line, or leaking the
player into his own baseline. Both are addressed rather than asserted away:

- **Leakage** — line baseline recomputed leave-one-out. Rebuilt LINX ranks **0.991**
  against the original, so the concern had no material effect.
- **Travels across lines** — when a back changes teams, LINX is as stable (r = 0.294)
  as when he stays (0.284). If it measured blocking, a new line would break that.
- **Not the line** — r(LINX, ESPN team Run Block Win Rate) = **0.031**, and 75% of LINX
  carries no line term by construction.
- **Leave-one-season-out** — fold correlations 0.057 to 0.549, mean 0.340. One weak fold
  (2024), which is why we call the signal "suggestive."
- **Weight sensitivity** — four alternative weightings rank-correlate 0.990–0.996 with
  45/30/25. No arbitrary weight choice drives the result.

## Why the weights are hand-set rather than fitted

Because fitting them didn't help. On a strict train-on-2018–2022, test-on-2024–25 split,
Ridge-learned weights scored 0.213 against the theory weights' 0.214. The fitted version
looked better in-sample (train r = 0.33) and collapsed out-of-sample — textbook
overfitting. We report the fitted attempt as evidence *for* 45/30/25 rather than hiding it.

This pattern recurred across the wider project: nearly every sophisticated adjustment we
tried failed its blind test, and the simple version won. The one exception was *deleting*
components that carried no signal, which generalized fine. Re-tuning live components did not.

## Repository layout

```
scripts/verify_all.py          rebuilds LINX and re-derives every headline number
scripts/verify_robustness.py   the peer-review checks above
data/                          all inputs, plus data_provenance.csv classifying each file
docs/LINX_METHODOLOGY_AND_RESULTS_DOSSIER.md   full methodology and stated limitations
docs/REFEREE_PROMPT.md         a skeptical-reviewer prompt; run it against this repo
```

`data/data_provenance.csv` classifies every file as frozen historical record or derived
output. The metric is computed from historical record only — no market data, no judgment
calls, no hand-entered adjustments enter LINX.

## Data sources

Pro Football Reference (advanced rushing, 2018–2025), NFL Next Gen Stats via nflverse
(Rushing Yards Over Expected), ESPN (team Run Block Win Rate). All public.

## Reproducibility

No internet access, no API keys, no hardcoded paths — the scripts read the CSVs in
`data/`. If a number does not reproduce, that is a real finding and we want to hear it.
