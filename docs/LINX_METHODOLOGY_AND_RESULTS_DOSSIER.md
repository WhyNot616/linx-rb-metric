# LINX — Methodology & Results Dossier (for independent validity/reliability audit)

**Purpose:** a self-contained technical record so a third party (human or AI) can rigorously
check whether the statistics are sound — leakage, overfitting, p-hacking, sample size, overstated
claims. Written to be audited critically. All figures are the actual computed results; caveats are
stated where results are modest, in-sample, or uncertain.

---

## 1. The metric
**LINX** (Line-Independent Rushing Index) rates an NFL running back's skill independent of his
offensive line:
`LINX = 0.45·z(YAC/att) + 0.30·z(BrokenTackle rate) + 0.25·z(OL_adj_YBC/att)`
- z(·) = standardized (mean 0, sd 1) **within each season** across qualifying RBs.
- YAC/att = yards after contact per attempt; BrokenTackle rate = broken tackles / attempt.
- OL_adj_YBC/att = a back's yards-before-contact/att minus his **team's carry-weighted YBC/att**
  (isolates the runner vs his line).
- Weights 45/30/25 are **theory-based**, then stress-tested (see §4).
- Threshold: 100+ carries to qualify.
- **SCOPE:** LINX measures *rushing* skill (efficiency + tackle-breaking) independent of the line.
  It deliberately ignores receiving. It is NOT a measure of total RB/fantasy value — receiving is
  handled separately in the fantasy engine (§8).

## 2. Data
- Source: Pro Football Reference advanced rushing + fantasy tables; NFL Next Gen Stats (RYOE);
  ESPN Run Block Win Rate; Pro Football Network OL grades. Public, verifiable.
- Span: 2018–2025 (8 seasons; earliest year advanced rushing data exists).
- Samples: **371** qualifying player-seasons; **211** year-over-year (YoY) pairs (same player,
  consecutive seasons, both 100+ carries); **693** RB fantasy-seasons; **401** fantasy YoY pairs.
- All correlations are Pearson r; R² = variance explained; p = significance.

## 3. Validity results
| Test | Result | n | Note |
|---|---|---|---|
| Within-season: LINX ↔ YPC-above-team-avg | r=0.632, 95% CI [0.567, 0.689] | 371 | **PART-WHOLE** — see caveat |
| YoY stability (single-year LINX) | r=0.316, p<0.0001 | 211 | up from 0.20 on prior 4-yr build |
| Multiple reg: LINX_t+1 ~ LINX_t + OL_delta + age | R²=0.157, F p<0.0001 | 211 | LINX_t & OL_delta significant; age not |

**IMPORTANT (part-whole correlation):** the 0.632 is a *contemporaneous* correlation between LINX
and a target (YPC-above-team) that shares LINX's own inputs (YAC/att, YBC/att). So it is strong
partly *by construction* — it is NOT the headline evidence of skill capture. The genuine, honest
validity is the **out-of-sample predictive r ≈ 0.291** (§5). Lead any abstract with 0.291, not 0.632.

## 4. Weights: tested and NOT changed (overfitting guard)
- Ridge regression (CV-tuned) explored data-driven weights (e.g., predictive ≈33/3/64).
- **Blind holdout** (train 2018–2023, predict sealed 2024–2025): all weightings converged to
  test r≈0.21 — the data-driven weights **overfit** and did NOT beat 45/30/25 out-of-sample.
- Decision: keep 45/30/25; cite Ridge as evidence *for* the theory-based weights.

## 5. Stabilization (the "year-to-year" upgrade)
- Method: 3-season window, recency decay 0.5, empirical-Bayes shrink K=200. **Hyper-params tuned
  on training data only**, then blind-tested.
- Blind predictive r (next-yr YPC-above): 0.214 → **0.291, 95% CI [0.054, 0.496], n=67**. Real but
  MODEST, and the CI is wide (small blind sample).
- Bootstrap (10,000×) of the improvement over single-year: median +0.076, 95% CI **[−0.035, +0.195]**.
  Because the CI crosses zero, the honest conclusion is **suggestive but NOT statistically significant**
  at α=0.05 — requires a larger holdout to confirm.
- (Removed from results: a "year-to-year self-stability = 0.742" figure. That number is a mechanical
  auto-correlation of overlapping 3-year averages — consecutive windows share 2 of 3 input years — and
  does NOT measure predictive stability. It is excluded to avoid a misleading impression.)

## 6. External benchmark vs NFL Next Gen Stats RYOE
- Matched 370/371 backs. Within-season LINX↔RYOE/att **r=0.715** (~51% shared) → related, not redundant.
- LINX↔YPC-above (0.633) > RYOE↔YPC-above (0.586).
- Predict next-yr YPC-above (full-sample pairwise): stabilized LINX **0.258** vs RYOE **0.141**.
- **STRICT HOLDOUT (train 2018–2023 → sealed 2024–2025, n_test=67):** out-of-sample TEST R²:
  LINX-only **+0.078**, RYOE-only **−0.025** (RYOE alone did not beat the mean out-of-sample),
  LINX+RYOE +0.057. **LINX adds +0.082 over RYOE; RYOE adds −0.021 over LINX** (i.e., adding RYOE
  to LINX does not help). → On a proper holdout, LINX carries predictive signal RYOE lacks, and RYOE
  adds no incremental value on top of LINX.
- **Wording:** do NOT say "subsumes." Defensible statement: *"LINX out-predicts RYOE out-of-sample,
  and RYOE adds no incremental value on top of LINX (strict 2018–23 → 2024–25 holdout)."*
- **Caveat:** n_test=67 is small, so the magnitudes are noisy; the direction (favoring LINX) is
  consistent across full-sample and holdout, but treat the exact R² values as uncertain.

## 7. Robustness checks
- **OL isolation:** built a two-way (runner vs line) decomposition + shrinkage on all 915 RBs;
  team-line estimates agree with ESPN Run Block Win Rate at r≈0.24 (pooled 2023–25). But swapping
  it into LINX did NOT beat the simple team-average on blind prediction (0.259 vs 0.245) → kept simple.
- **Injury/availability:** games-missed adds only +0.002 R² beyond LINX (partial corr 0.05, p=0.47);
  adds 0.000 to blind test; injuries don't repeat year-to-year (r=−0.08). → no adjustment; LINX
  unbiased by playing hurt.
- Pattern: every fancier variant was blind-tested; only stabilization + the NGS benchmark "won."

## 8. Fantasy engine (Product 2)
- Ridge regression, target = next-year PPR points/game. 401 YoY pairs.
- Weights (standardized): prior PPR/g +1.86, carries/g +1.11, receiving +0.64, **LINX +0.61**, age
  −0.68, games_missed −0.11 (targets & rush-TD-rate ≈0).
- CV R² = 0.471; **blind (2024–25) R² = 0.523, 95% CI [0.396, 0.620]** (n_test=114) vs naive
  "same as last year" R² ≈ 0.43. Blind CI is solidly positive.
- **Why blind ≥ train (checked):** test-set target SD (5.40) is slightly HIGHER than train (5.22),
  so the blind R² is NOT inflated by an "easier"/lower-variance test set — it reflects genuine
  generalization on a favorable split, not a variance artifact or leak.
- **Overfit audit:** in-sample R² 0.502 vs CV 0.471 (gap 0.03); blind R² (0.523) ≥ train (0.489);
  Ridge beat unregularized OLS on blind; the 5 meaningful coefficients were sign-stable across
  2,000 bootstraps (targets/TD-rate/games-missed were near-zero & unstable → non-contributors).
- **LINX's incremental value to fantasy = +0.015 R²** beyond box-score volume/role. Real but small.

## 9. Explicitly NOT validated (flagged as such)
- **Rookie proxy:** college-based estimate + depth-chart-average carries. NOT the NFL LINX; no
  blind test possible (no NFL data). Directional only.
- **2026 projections:** role-stable from 2025 usage + an offseason context overlay; not a
  re-estimated forecast per player-role.

## 10. Honest limitations (audit these hardest)
- RB year-to-year prediction has a **low ceiling** for everyone (blind r≈0.21–0.29, small R²).
- LINX's incremental fantasy value over raw volume is small (+0.015 R²).
- Samples modest (211 YoY pairs); several key results are correlational.
- The 0.74 self-stability is partly mechanical (overlapping windows) — do not headline it.
- The NGS comparison is now ALSO shown on a strict holdout (§6); full-sample and holdout agree in
  direction, but the holdout n_test=67 is small.
- Multi-team players: the LINX qualifying sample contains **0 "2TM/3TM" aggregate rows** — it uses
  single-team split rows, assigning a traded player to the team where he reached 100+ carries. So
  the 2TM-bias concern does not apply to the LINX sample.
- LINX ignores receiving by design (§1 scope) — it is a rushing-skill metric, not total RB value.
- Data via third-party sources; note PFR (manual charting) and NGS (tracking) may define YAC slightly
  differently, which could affect the LINX↔RYOE correlation magnitude.

## 11. Reproducibility
Every result comes from saved Python scripts (`step*.py`) + public-source CSVs in this folder.
Key files: linx_scores_2018_2025.csv, linx_stabilized_scores.csv, linx_yoy_pairs.csv,
ngs_ryoe_2018_2025.csv, pfr_fantasy_rb_2018_2025.csv, fantasy_engine_model.json, and the
summary .txt files. An independent party can re-run and confirm every number.
