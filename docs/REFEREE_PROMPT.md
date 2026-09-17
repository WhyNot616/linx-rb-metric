# Independent Audit Request — The LINX Suite (RB + WR fantasy-football metrics)

You are a skeptical, statistically literate reviewer. Your job is to try to break this
work, not to be nice to it. Please verify the numbers, then judge whether the claims are
calibrated (i.e., whether the author claims exactly what the evidence supports, no more).

## What the project is
Two products built on 8 seasons of public NFL data (2018–2025):
1. **Skill metrics** that isolate a player's own ability from his situation.
   - **LINX** (running back): `0.45·z(yards-after-contact/att) + 0.30·z(broken-tackle rate) + 0.25·z(line-adjusted yards-before-contact/att)`, z-scored within season, 100-carry minimum. The line-adjustment subtracts each back's own team's carry-weighted yards-before-contact, so what's left is the back beating his own blocking.
   - **WRX v3** (wide receiver, the shipped version): `0.70·z(catch-over-expected) + 0.20·z(broken-tackle rate) + 0.10·z(-drop rate)`. Catch-over-expected is a depth-adjusted catch-rate residual the author computes (a proxy, labeled as such).
     - **An earlier version (v1) of this metric weighted separation at 0.30 and YAC-over-expected at 0.20. Both were tested and removed.** Separation is real NFL Next Gen Stats tracking data and is the most *stable* input measured (year-over-year r = 0.612) — and it does not predict next-season fantasy points (r = −0.02, p = 0.70; +0.001 R² on top of the other inputs). YAC-over-expected carried no signal either (r = +0.033, p = 0.52). **A central thing to probe is whether removing them was justified or was post-hoc selection.**
     - Note the trade this makes: v3 is *less* stable year over year than v1 (self-r 0.308 vs 0.420) but predicts better (see below). The author's position is that stability is not predictive value. Is that defensible, or is the drop in stability a warning sign?
2. A **Ridge-regression projection engine** that turns skill + volume + role + age into projected fantasy points.

## How to verify (please actually run these)
All scripts are self-contained and read the CSVs sitting next to them. Requires Python 3 with pandas, numpy, scipy, scikit-learn.
```
python3 verify_all.py         # reproduces the running-back numbers
python3 verify_wr.py          # reproduces the wide-receiver numbers, v1 and shipped v3
python3 verify_robustness.py  # the extra peer-review checks (leakage, line-independence, LOSO, sensitivity)
```
Each prints `computed` next to `claimed`. Confirm they match (diffs < 0.01 are rounding).

## Robustness checks already run (please confirm and try to break)
An earlier reviewer worried the line adjustment might leak the player into his own baseline, and that LINX might just be tracking the offensive line. Both are addressed in `verify_robustness.py`:
- **Leakage-proof rebuild:** the line baseline is recomputed excluding the player's own carries (leave-one-out). Rebuilt LINX ranks 0.991 identical to the original, so the concern had no material effect.
- **Travels across offensive lines:** when a back changes teams, LINX is as stable (r = 0.294) as when he stays (0.284). If it measured blocking, a new line would break that.
- **Not just the line:** LINX vs team Run Block Win Rate r = 0.031 (near zero); and 75% of LINX has no line term by construction.
- **Leave-one-season-out:** fold correlations mean 0.340 (range 0.057 to 0.549; one weak fold, hence "suggestive").
- **Weight sensitivity:** alternative weightings rank-correlate 0.99+ with 45/30/25.
The author frames LINX as a **line-adjusted, predictive metric and a supported hypothesis, not a proven measurement of intrinsic skill.** Is that framing now appropriately calibrated?

## The claims to check (do the numbers support these, and only these?)
Running backs (LINX):
- Within-season validity r = 0.632 vs "yards/carry above team." **The author flags this as part-whole overlap and uses it only as a sanity check, not as predictive evidence.** Is that framing honest?
- Year-over-year stability r = 0.316; rises to blind r = 0.291 after multi-year stabilization (empirical-Bayes shrinkage, 3-yr decay window). Author calls the 0.291 "suggestive, not proven" due to a wide CI. Agree?
- Weights not overfit: theory weights 45/30/25 tie Ridge-learned weights out of sample (0.214 vs 0.213). Fair conclusion?
- Beats the NFL's own RYOE out of sample at predicting next season: LINX 0.258 vs RYOE 0.141.
- Games-missed adds +0.002 R² on top of LINX (i.e., not just measuring health).

Wide receivers (WRX v3 + engine):
- Skill stability: WRX v3 self-r = 0.308; the superseded v1 weighting 0.420; separation alone 0.612 (n=398). The author argues the shipped metric being *less* stable is acceptable because stability ≠ predictive value. Test that argument.
- WRX v3 holdout (weights fixed on 2018–2022, scored on 2023–24 only, n=116): v3 r = +0.301, croe alone +0.262, superseded v1 weighting +0.224. **The author's claim is that the gain comes from deleting an input with no signal, not from re-tuning — and explicitly contrasts this with LINX, where fitted weights overfit and hand-set weights won. Is that distinction real or convenient?**
- Fantasy engine blind holdout (train ≤2022, test 2024-25, n=59): R² = 0.33, r = 0.63; naive "repeat last year" baseline R² = −0.12.
- Engine beats every single public stat on the same blind test (0.63 vs air-yards-share 0.40 vs catch-rate 0.26 vs separation −0.15).

## Specifically probe for
1. **Data leakage / look-ahead**: any way training data leaked into the blind test?
2. **Overfitting**: is the blind performance actually out-of-sample?
3. **Part-whole / circularity**: beyond the 0.632 the author already flagged, any other place a metric is graded against its own ingredients?
4. **Sample size**: the WR blind test is n=59 pairs; the RB stabilized signal is small. Are the confidence claims appropriately hedged?
5. **Overclaiming**: anywhere the prose says more than the number supports?
6. **The rookie projections are explicitly college-based proxies, not validated** — confirm they are not being passed off as validated.
7. **Post-hoc component selection**: WRX dropped two of its five inputs after testing them. Was that a principled deletion of dead components, or selection on the test data? The author claims the former and points to the contrasting LINX result (where fitted weights lost). Check whether the holdout used for the WRX decision is genuinely separate from the fit.
8. **Version drift**: the shipped metrics are WRX v3 and QBX v3. Confirm the scripts, this prompt, and the public site all describe the *same* version. An earlier release of this package described WRX v1 while shipping v3 — flag any remaining inconsistency you find.

## Please return
- A table of `claim → reproduced? (yes/no) → your value`.
- A list of any statistical problems you found (leakage, overfitting, circularity, overclaiming), or "none found."
- A verdict: are the headline claims **supported, overstated, or understated**?
- Any wording you'd change to make it more defensible before publication.
