# Experiment Log — TimesFM Per-Sector LoRA Benchmark

> Paper-ready running record. Definitions here are written to lift directly into
> the Methods section. Sections marked _(filled after run)_ are populated as each
> phase completes. Located in `paper/` because `doc/` is git-ignored in this repo.

Last updated: 2026-06-03.

---

## 1. Motivation & central questions

An early LoRA adapter reported **~80% directional accuracy**; per-sector adapters
then reported **~50%**. Diagnosis: ~80% is almost certainly a **base-rate / trend
artifact**, not skill —

- Directional accuracy was compared to an implicit 50% coin flip, but equities are
  not 50/50: over a long horizon (h=128 ≈ 6 months) in a bull market, price is *up*
  in ~75–85% of windows. An "always-up" rule scores ~80% with zero skill.
- Early data started 2014 (a near-uninterrupted bull); the per-sector run started
  2005 (includes 2008–09), lowering the up base-rate toward ~55%.
- The earlier pipeline early-stopped on the evaluation window (model-selection leak)
  and look-ahead normalization was only fixed in a later iteration.
- The reference work (Fu, Hirano & Imajo, 2024, arXiv:2412.09880) reports ~54% at
  h=2 — the realistic ceiling.

**The benchmark is built to answer, defensibly:**
1. Was the 80% just the equity uptrend? (excess-over-base-rate ≈ 0?)
2. Does LoRA fine-tuning beat **zero-shot** TimesFM?
3. Does **per-sector** specialization beat a **pooled** equity adapter?
4. Do sector adapters **generalize to held-out tickers** (learned behavior, not
   memorized symbols)?
5. Are the results **statistically defensible**?

---

## 2. Data provenance

- Source: yfinance, `auto_adjust=True`; price field stored as **`adjusted_close`**.
- Universe: S&P 500 constituents (current snapshot) + 11 SPDR sector ETFs (anchors).
- Span: 2005-01-01 → 2026-01-01, daily.
- Frozen artifact: `data/frozen/<version>/` — `prices.parquet`/`prices.csv.gz`,
  `universe.json` (per-ticker sector/category/date-range, sha256), `environment.json`,
  `requirements_freeze.txt`. Loaded via `finetune/data_frozen.py` with checksum verify.
- **Realized (2026-06-04 fetch):** version
  `sp500_2005-01-01_2026-01-01_f2026-06-04` · **501 stocks + 11 ETFs** (514 requested,
  2 dropped too-short) · **11 sectors** · 2,465,821 rows · `prices.csv.gz` **24.1 MB**
  (pyarrow absent locally → gzip-CSV; under GitHub limits, no LFS) · series length
  median 5283 (≈21y), min 443 · sha256 `c4c3564d66b0670c…`.

- **Nasdaq-100 extension (2026-06-16 fetch; advisor request).** To test whether a
  tech-heavy universe improves the pooled adapter, the **same freeze pipeline**
  (`scripts/freeze_data.py --universe nasdaq100`; identical window, `auto_adjust`,
  `min_len=252`) produced version `nasdaq100_2005-01-01_2026-01-01_f2026-06-16` —
  **100 stocks + QQQ** (Nasdaq-100 ETF as index anchor; 101 requested, SNDK dropped
  too-short) · **10 sectors** · 459,852 rows · `prices.csv.gz` · sha256
  `cf2ae0dafad95458…`. **Universe + sector source = the advisor's `simofi` catalog**
  (`simofi/data/universes.json` `QQQ` membership + `simofi/data/stocks.json` sector
  tags), read via `finetune.data_collector._get_nasdaq100_from_simofi`; this replaces
  the earlier brittle Wikipedia ICB scrape (prior version `…_f2026-06-08`, sha256
  `77c3a81a…`, now superseded). simofi tags sectors in the **Yahoo scheme**, mapped
  to our codes via `YAHOO_SECTOR_MAP` so NASDAQ and S&P 500 share one taxonomy; all
  101 members carry a sector (none "unknown"). Sector mix: tech 41, cons_disc 11,
  comms 11, industrials 11, healthcare 10, cons_staples 8, utilities 4, energy 2,
  materials 1, financials 1. These labels are used **only** to stratify the held-out
  split. Thin sectors (financials/materials n=1, energy n=2) reserve few/no held-out
  names. **Scope: pooled adapter only** — Nasdaq-100 pooled vs S&P 500 pooled,
  method fixed; per-sector NASDAQ adapters are not viable given the thin tails.

> **Limitation (survivorship bias):** current membership snapshot, not point-in-time
> constituents. Stated; results not overclaimed beyond it.

---

## 3. Splits (`finetune/splits.py`)

**Time — walk-forward, expanding, train → validation → test.** Validation is the
ONLY signal for early stopping / model selection; the test window is never used for
selection. Default (`walk_forward_folds`, n_folds=3, val_years=1, test_years=2):

| Fold | Train | Validation | Test |
|---|---|---|---|
| 0 | 2005-01-01 → 2019-01-01 | 2019 → 2020 | 2020 → 2022 |
| 1 | 2005-01-01 → 2021-01-01 | 2021 → 2022 | 2022 → 2024 |
| 2 | 2005-01-01 → 2023-01-01 | 2023 → 2024 | 2024 → 2026 |

**Symbol — held-out tickers** (`holdout_split`): per-sector stratified ~80/20,
seeded (default 42), **fixed across folds** so held-out names are never trained in
any fold. ETFs are excluded from the holdout pool (always "seen", reported as their
own category). Sectors too small to reserve a held-out set are flagged
(`sectors_without_holdout`) and carry wider CIs. Every method is reported on **seen**
and **held_out** splits.

**Realized (seed=42, frac=0.20):** 394 seen / 107 held-out stocks; all 11 sectors
have a non-empty held-out set (smallest: energy n=21 → 5 held-out;
`sectors_without_holdout` is empty).

---

## 4. Normalization protocol

> **Training** normalizers (`LogNormalizer`, log + per-series z-score) are fit only
> on the **train** slice. **Evaluation** normalizers are fit only on **pre-target
> history**, never on any target-window observation: for the **validation** window
> that is the **train** period; for the **test** window that is **train +
> validation**. Applied consistently across zero-shot, pooled, per-sector, and naive
> methods, identically to seen and held-out tickers (no asymmetry). This mirrors
> deployment (you normalize a ticker from its past, then predict).

Direction is invariant to this monotone transform, so directional metrics may be
computed in normalized space; **returns/Sharpe use inverse-transformed prices.**

---

## 5. Models & training _(training protocol filled after Colab runs)_

- Base: `google/timesfm-2.5-200m-pytorch` (Das et al., 2024), patched decoder-only,
  RevIN internal normalization (Kim et al., 2021), 10-channel quantile head.
- Adapter: LoRA (Hu et al., 2021) on `stacked_xf.*` linear layers only;
  `create_lora_model` (rank/alpha/dropout from `finetune/config.py`).
- Forward pass: `decode_forward` (RevIN normalize → backbone → de-RevIN), shared by
  base (zero-shot) and adapted models.
- Early stopping on the **validation** window; adapters saved under
  `adapters/walkforward/<version>/fold_<k>/<sector|pooled>/`.
- **Zero-shot isolation:** a dedicated base instance (no PEFT) serves the zero-shot
  baseline; an assertion (`torch.allclose`, atol≈1e-5) confirms its outputs are
  unaffected by adapter loading.

---

## 6. Naive baselines (`finetune/metrics.py`)

- **always_up** — predicts positive direction every window (the base rate).
- **random_walk** — price forecast = last context value ⇒ no directional call;
  ties are **excluded** from directional accuracy and earn **0 return** in trading.
- **persistence** — repeats the sign of the last context return.
- **AR(1)** — fit on context returns only; **directly predicts the h-period return**
  (not recursive one-step), for fairness with the benchmark horizon.

---

## 7. Metrics (`finetune/metrics.py`)

**Directional** (windows with a directional call and non-flat actual):
`acc`, `always_up_acc` (= base rate on the same windows), `excess_acc = acc −
always_up_acc`, balanced accuracy (Brodersen et al., 2010), Matthews correlation
(Matthews, 1975), `n_windows`.

**Point** (price space, **per-ticker then macro-averaged** so high-priced names
don't dominate): MAE, RMSE, sMAPE (fraction in [0,2]), and **MASE** (Hyndman &
Koehler, 2006) scaled by the in-sample one-step random-walk MAE.

**Calibration** (quantile head): per-level empirical **coverage** vs nominal, pinball
loss, and CRPS ≈ 2·mean-level pinball (Gneiting & Raftery, 2007).

**Economic — real returns:** per non-overlapping h-day trade, signal = sign(pred);
market return `P_{t+h}/P_t − 1`; strategy return = signal·market. **Annualized
Sharpe = mean(r)/std(r)·sqrt(252/h)** (sample std), gross and transaction-cost-
adjusted; plus max drawdown, hit rate, turnover, `n_trades`.

---

## 8. Significance & pre-registration

- **excess_acc** — paired **block bootstrap** CI (resample whole blocks by
  ticker/date; windows are autocorrelated) and **McNemar** test (McNemar, 1947) on
  paired per-window correctness vs always-up.
- **Forecast error** — **Diebold-Mariano** (Diebold & Mariano, 1995; Newey-West LRV,
  lag h−1) for: pooled vs zero-shot, per-sector vs zero-shot, **per-sector vs
  pooled**. Convention: negative DM ⇒ model better.
- **Multiple comparisons:** **Benjamini-Hochberg FDR** (Benjamini & Hochberg, 1995)
  over the exploratory family.

**Pre-registered hypotheses:**
- **Primary (confirmatory):** per-sector vs pooled on **held-out stocks (excluding
  ETFs) at h=128** — DM and paired-bootstrap excess_acc.
- **Secondary (exploratory):** all other horizons/sectors/methods, BH-FDR controlled.

---

## 9. Results _(filled after Colab runs)_

Canonical tables → `results/benchmark/<version>/`:
- **A — directional/trading (headline):** method · split · category · horizon ·
  n_windows · n_trades · acc · always_up_acc · excess_acc · excess_acc_CI ·
  balanced_acc · MCC · Sharpe · Sharpe_CI · maxDD · hit_rate.
- **B — point-forecast (macro-averaged):** + MAE · RMSE · sMAPE · MASE.
- **C — calibration:** quantile_level · nominal · empirical_coverage · pinball.
- **D — significance:** comparison · split · horizon · test · statistic · p_or_CI ·
  fdr_adjusted.

Diagnostic interpretation (neutral): high acc with **excess_acc ≈ 0** ⇒ the 80% was
base-rate/trend; **excess_acc > 0 & significant** ⇒ genuine skill; **per-sector >
pooled on held-out** ⇒ learned behavior over memorization.

### 9.1 Nasdaq-100 pooled (2026-06-16)

First full walk-forward run in this framework: version
`nasdaq100_2005-01-01_2026-01-01_f2026-06-16`, `pooled_only`, 3 folds, method
unchanged (rank 32, alpha 64, batch 512, h=128/ctx 512). Tables in
`result/nasdaq_100/{raw.json,tables.md}`. Methods scored: `pooled` (LoRA),
`zero_shot` (base TimesFM), and naive `always_up` / `persistence` / `ar1`
(`random_walk` makes no directional call, so its directional cells are empty by
design).

**Directional accuracy — held-out stocks** (fold-mean; n≈207/horizon; excess =
pooled − always_up):

| horizon | pooled | zero_shot | always_up | pooled excess |
|---|---|---|---|---|
| 2 | 0.471 | 0.399 | 0.446 | **+0.025** |
| 4 | 0.468 | 0.411 | 0.418 | **+0.051** |
| 8 | 0.515 | 0.524 | 0.577 | −0.062 |
| 16 | 0.511 | 0.528 | 0.545 | −0.034 |
| 32 | 0.520 | 0.560 | 0.623 | −0.103 |
| 64 | 0.473 | 0.530 | 0.541 | −0.068 |
| 128 | 0.634 | 0.559 | 0.711 | −0.077 |

Findings (neutral):
1. **No directional skill over the trend at h≥8.** `excess_acc` is negative at every
   horizon ≥8 (worst −0.103 at h=32). The only positive excess is at h=2 (+0.025)
   and h=4 (+0.051), where `always_up` itself is weak; Sharpe at those horizons is
   negative, so the edge is not tradeable. This is the **predicted base-rate/trend
   pattern** — at h=128 `always_up` alone scores 0.711 on the (uptrending) Nasdaq-100.
2. **LoRA does beat zero-shot at the long horizon.** Pooled h=128 = 0.634 vs zero-shot
   0.559 (+7.5 pts) on held-out stocks (seen: 0.564 vs 0.492, +7.2 pts); also wins at
   h=2/4. It is comparable-to-worse at the mid horizons (8–64).
3. **Point forecasts not improved.** Pooled MAE ≥ zero-shot everywhere (held-out
   stock 27.50 vs 26.44; seen 25.33 vs 23.32) — the adapter traded a little point
   accuracy for long-horizon direction.
4. **Calibration tails poor for both.** Nominal 0.05 → ~0.44 empirical coverage
   (pooled 0.4385, zero-shot 0.4039); mid-quantiles reasonable. A base-model trait
   LoRA does not fix.
5. **Long-horizon significance is not yet usable.** At h=128 the Diebold-Mariano
   statistics blow up (|stat| up to ~1.7e10) and max-drawdowns fall below −100%
   (e.g. −60 for pooled, −25636 for ar1) — a numerical overflow in the long-horizon
   return reconstruction on a few series, not a signal. Mid-horizon DM is mixed-sign
   across folds (inconclusive). **Fix the h=128 reconstruction before quoting any
   long-horizon Sharpe/DM.** _(Update 2026-06-29: the three root causes are fixed
   in eval code — see §10, 2026-06-29. The h=128 DM, max-drawdown, and persistence
   point cells in the tables above are from the **pre-fix** run and will be replaced
   when the corrected benchmark is re-run on GPU; the directional-accuracy table and
   findings 1–4 are unaffected, as direction is computed in normalized space.)_

**Headline:** consistent with the central thesis — the apparent long-horizon accuracy
is the equity uptrend, not skill (`excess_acc ≤ 0` for h≥8); fine-tuning yields a real
but modest improvement over zero-shot at h=128, and no point-forecast gain.

> **Comparison status:** No S&P 500 pooled run exists in this framework yet. The
> archived `sector_vs_pooled*.md` files are the **prior** (single-split, no-baseline,
> no-held-out) methodology and are **not comparable**. To answer "is Nasdaq better
> than S&P," run `rb.run(version='sp500_2005-01-01_2026-01-01_f2026-06-04',
> pooled_only=True)` and compare these same cells.

### 9.2 Clean seeded two-universe run (2026-06-30) — supersedes §9.1 numbers

Both universes re-run **seeded** (seed 42, commit `796f0e7`, clean tree, A100,
torch 2.11.0+cu128) with the best-val reload, the bounded drawdown, the
normalized-space + lag-capped DM, and persistence excluded from the point table.
Artifacts: `doc/result/6-30-1-13/{nasdaq,sp500}_{raw.json,run_meta.json,tables.md}`;
figures: `paper/figures/fig_{excess_acc,accuracy_vs_baserate,calibration,point_mae}.png`;
write-up: `paper/DRAFT.md`.

**Headline (held-out stocks, fold-mean):** the negative result **replicates across
both universes**. Pooled excess_acc is centred on zero with CIs spanning zero at every
horizon and **negative at h=128** (NASDAQ −0.081, S&P −0.017); always-up alone scores
0.710 / 0.658 at h=128, above pooled's 0.630 / 0.641 — i.e. **no directional skill over
the base rate**. Zero-shot is below the base rate everywhere. The only significant
fine-tuning effect is **lower point error than zero-shot** (DM negative, FDR-significant
16/21 S&P-seen, 7/21 NASDAQ-seen cells; held-out MAE pooled 25.15<26.44 NASDAQ,
15.15<16.31 S&P) — but pooled does **not** beat naive always-up on MAE and has no
tradeable edge. Calibration tails poor for both (nominal 0.05 → ~0.44). Fine-tuning
overfits early (best epoch {5,16,3} NASDAQ / {1,2,1} S&P of 44). h=128 is **underpowered**
(McNemar discordant pairs/fold {3,10,10} NASDAQ, {5,5,20} S&P) → no h=128 significance
claim. Per-sector dropped (NASDAQ strata too thin) → the NASDAQ-vs-S&P comparison is
**exploratory** and its value is the cross-universe **replication of the null**, not a
"which is better" claim (confounded by size/sector/price).

---

## 10. Decisions & changelog

- **2026-06-03** — Diagnosed 80%→50% as base-rate artifact, not regression. Approved
  paper-grade redesign: frozen data + walk-forward train/val/test × held-out tickers
  + zero-shot/naive baselines + real-return metrics + paired/block significance +
  pre-registration. Built `finetune/{splits,metrics,data_frozen}.py`,
  `scripts/freeze_data.py`, `tests/` (26 + 4 tests passing). Ran data freeze
  (commit `2a28ab8`, branch `paper-benchmark`).
- **2026-06-03** — Built the evaluation harness: `finetune/benchmark.py` (windowing,
  naive baselines, model path via `decode_forward`, zero-shot isolation, Tables A/B/C
  scoring with block-bootstrap excess-accuracy + Sharpe CIs); `finetune/run_benchmark.py`
  (walk-forward orchestrator — per fold trains pooled + 11 sector adapters
  early-stopping on validation, evaluates zero-shot/pooled/per-sector/naive on the
  test window for seen+held_out over identical windows, Diebold-Mariano + McNemar
  significance with BH-FDR, writes `results/benchmark/<version>/raw.json`);
  `scripts/render_tables.py` (Tables A–D markdown). **42 CPU tests pass.** GPU
  smoke-test (fold 0) and full walk-forward run pending on Colab.
- **2026-06-07** — **Nasdaq-100 pooled comparison (advisor request).** Goal: test if
  training the LoRA on a tech-heavy Nasdaq-100 universe beats the S&P 500 universe,
  **holding the method fixed**. Verified the method is unchanged: `config.py`,
  `trainer.py`, `model_setup.py`, `run_benchmark.py` were all last modified in commit
  `c942262` (the S&P 500 run), working tree clean — so rank (32 / 16 small), alpha
  (64), dropout (0.05), batch (512), AdamW(lr 1e-4, wd 0.01)/cosine-warm-restarts,
  grad-clip 1.0, epochs 80 / patience 15 / min 30, financial_loss (mse + dir 0.3),
  context 512 / horizon 128, LogNormalizer+RevIN are all identical; only `--version`
  (the data) changes. Added: `_get_nasdaq100_with_sectors` (ICB crosswalk) +
  `freeze_data.py --universe {sp500,nasdaq100}`; froze the Nasdaq-100 artifact (above);
  `run_benchmark.py --pooled-only` (single pooled adapter on seen stocks, scored on
  seen+held_out vs zero-shot/naive — reuses `train_adapter`/`fine_tune`/`config`
  unchanged, skips per-sector); `notebooks/run_nasdaq_pooled_colab.ipynb`. **42 CPU
  tests still pass.** GPU run pending on Colab:
  `rb.run(version='nasdaq100_2005-01-01_2026-01-01_f2026-06-08', pooled_only=True)`.
- **2026-06-16** — **Nasdaq-100 universe re-sourced from advisor's `simofi` catalog.**
  Replaced the brittle Wikipedia ICB scrape with `simofi/data/{universes,stocks}.json`
  as the authoritative NASDAQ-100 membership + sector source (new
  `finetune.data_collector._get_nasdaq100_from_simofi`; Wikipedia scrape kept as
  `_get_nasdaq100_from_wikipedia` fallback; `YAHOO_SECTOR_MAP` Yahoo→code crosswalk so
  NASDAQ and S&P share one taxonomy). Re-froze → version
  `nasdaq100_2005-01-01_2026-01-01_f2026-06-16` (100 stocks + QQQ, **10 sectors**, all
  members sector-labeled, sha256 `cf2ae0da…`), superseding `…_f2026-06-08`. **Method
  still unchanged** (no edits to config/trainer/model_setup/run_benchmark). Notebook
  `VERSION` updated. GPU run pending on Colab:
  `rb.run(version='nasdaq100_2005-01-01_2026-01-01_f2026-06-16', pooled_only=True)`.
- **2026-06-16** — **Bug fix: walk-forward training crashed on first GPU run.**
  The Colab smoke test (`rb.run(..., pooled_only=True, smoke=True)`) raised
  `AttributeError: 'TrainingConfig' object has no attribute 'asset_class'` at
  `trainer.py:225`, where `fine_tune` checkpoints best-val weights to
  `save_dir/<asset_class>_best`. `run_benchmark.train_adapter` copied the config but
  never set `asset_class`/`save_dir` (the walk-forward & deployable paths had never
  been run on GPU). Fixed by deriving both from the adapter's `save_path` in
  `train_adapter` (mirrors `finetune/main.py`); `trainer.py`/`config.py` left
  **byte-for-byte unchanged**, so rank/batch/optimizer/loss are identical — this is
  an orchestration fix, not a method change. Eval loads adapters by explicit path,
  so the new `<name>_best` checkpoint dirs are inert. 42 CPU tests still pass + a
  no-model check confirms the shared config is not mutated. Pushed to `nasdsq_fix`.
- **2026-06-16** — **First full Nasdaq-100 pooled walk-forward run completed** (3 folds,
  GPU). Results recorded in **§9.1** (`result/nasdaq_100/`). Headline: no directional
  skill over `always_up` at h≥8 (`excess_acc ≤ 0`), a modest +7.5 pt long-horizon gain
  over zero-shot at h=128, no point-forecast improvement — consistent with the 80% =
  trend thesis. Two follow-ups opened: (a) **h=128 numerical overflow** in the
  long-horizon return reconstruction (DM |stat|~1e10, maxDD < −100%) must be fixed
  before quoting long-horizon Sharpe/DM; (b) **S&P 500 pooled** must be run in this
  same framework (`sp500_2005-01-01_2026-01-01_f2026-06-04`, `pooled_only`) for a
  valid Nasdaq-vs-S&P comparison — the old `sector_vs_pooled*.md` is a different
  methodology and not comparable. Merged to `main`.
- **2026-06-29** — **Paper scope set to pooled NASDAQ-vs-S&P (method fixed); fixed
  the h=128 numerical overflow (follow-up (a)).** Three distinct evaluation-only
  bugs, all surfacing at the long horizon, were diagnosed and fixed — **no change
  to `trainer.py`/`config.py`, so the training method is identical**; only metrics
  and scoring change, which is why the corrected numbers require a re-run:
  1. **Max-drawdown explosion** (`metrics._max_drawdown`). `cumprod(1+r)` over a
     long/short trade series breaks when a **short** loses >100% (the underlying
     more than doubles): `1+r` goes negative, the equity curve flips sign, and the
     drawdown ratio diverges (−60 pooled, −25636 ar1). Fix: floor per-trade returns
     at −1.0 (margin-stop economics) before compounding and seed the curve at 1.0 →
     drawdown bounded to [−1, 0]. (Verified: a −240% trade now gives −1.0, not −1.6.)
  2. **DM statistic blow-up** (`benchmark.squared_error_at`). The DM loss was a
     **price-space** squared error; since `price = exp(z·std+mean)`, error grows
     exponentially in horizon and a few h=128 windows dominate the Newey-West
     variance (|stat|→1e10). Fix: compute the DM loss in **normalized (log-z)
     space** — per-series-standardized, monotone, sign-preserving, and both methods
     in a pair share the per-window normalizer so the paired differential is valid.
     (Verified: a case giving price-space |stat|=2.2e6 gives normalized |stat|=1.4.)
  3. **Persistence point divergence** (Table B). Persistence extrapolates the last
     log-return linearly for `horizon` steps, so its reconstructed price diverges
     geometrically (MAE ≈ 8e5 at h=128). Fix: exclude persistence from the
     point-forecast table (`benchmark.POINT_EXCLUDE`) — it is a directional/trading
     baseline only — and drop non-finite pairs in `point_metrics` as insurance.
  Directional metrics (excess_acc etc.) were never affected (computed in normalized
  space). Added 5 CPU regression tests (now **47 passing**, was 42). **Next: re-run
  the corrected benchmark on GPU for NASDAQ pooled, and run S&P pooled in the same
  framework, then refresh §9.1 and write up the NASDAQ-vs-S&P comparison.**
- **2026-06-29** — **Reproducibility hardening of the benchmark training path
  (validity/repro pass; hyperparameters unchanged).** An audit found the walk-forward
  training path was **unseeded** (LoRA A-matrix init via `get_peft_model`, DataLoader
  shuffle, dropout, the `random.randint` context mask) — only the holdout split (seed 42)
  was deterministic — and that `fine_tune` returned the **last-epoch** model though it
  checkpointed the **best-val** one, so the code contradicted the early-stopping methods
  claim. Fixes (no hyperparameter change): added `TrainingConfig.seed=42` + a
  `seed_everything` helper called in `train_adapter` **before** `create_lora_model()` (the
  LoRA-init site, so init is reproducible) and again atop `fine_tune` (training
  stochasticity), plus a seeded train-`DataLoader` generator; `fine_tune` now captures the
  best-val LoRA state in memory and **reloads it before returning** (guarded for the
  no-improvement case), so eval scores the *selected* model, and the real
  `best_epoch`/`n_epochs_run` flow up into a new `payload["training"]`. `run()` writes a
  **`run_meta.json`** manifest next to `raw.json` (seed, git commit + **dirty** flag,
  torch/CUDA/GPU, full `pip freeze`, hyperparameters, per-adapter best epoch).
  `torch.use_deterministic_algorithms` is deliberately NOT enabled (would crash TimesFM
  ops); results are **single-seed deterministic** (GPU atomics ⇒ ~1e-3 jitter), NOT
  multi-seed robust — multi-seed is future work. +4 CPU repro tests (**51 passing**). The
  Colab notebook gains a **reproducibility gate** (runs the smoke twice, asserts max
  |Δacc| < 1e-3) before the overnight runs. Both universes must be re-run on GPU with this
  code; the pre-fix/unseeded `result/nasdaq_100` numbers are superseded on rerun.
- **2026-07-10** — **Final results promoted into the repository; repo reorganized for
  publication (no method or number changes).** The three final GPU runs backing the paper
  (each `run_meta.json`: commit `703f181`, clean tree, seed 42, A100) are now committed
  under `results/`: `results/benchmark/sp500_2005-01-01_2026-01-01_f2026-06-04/`,
  `results/benchmark/nasdaq100_2005-01-01_2026-01-01_f2026-06-16/`, and
  `results/legacy/sp500_2005-01-01_2026-01-01_f2026-06-04_legacy_2014_2026/` (`raw.json` +
  `run_meta.json` + `tables.md`; the legacy run emits Table A only, so it has no
  `tables.md`). Files were copied byte-for-byte from the Colab downloads
  (`doc/result/6-30-5-01/`); the duplicate "(1)" download copies were verified
  hash-identical and dropped. Held-out headline numbers re-verified against the committed
  `raw.json` (every cell of the paper's excess-accuracy table reproduced; h=128: NASDAQ
  pooled 0.630 vs base 0.710, S&P pooled 0.641 vs 0.658, per-sector 0.599, legacy 0.626 vs
  0.704) — all match `paper/paper.tex`. Repo reorganization: `paper.tex` moved from
  `paper/figures/` to `paper/`, the compiled PDF renamed to
  `paper/when-directional-accuracy-lies.pdf`, and superseded material (old `DRAFT.md`,
  pre-benchmark notebooks and fix scripts, the unseeded 2026-06-16 `result/nasdaq_100`
  run, `sector_vs_pooled*.md`) moved to `archive/` with an index (`archive/README.md`).
  README rewritten around the paper (previous README preserved as
  `archive/README-legacy.md`).

---

## 11. Limitations

- Equity + sectors only (no forex/macro this round).
- Survivorship bias (current membership snapshot).
- Small sectors ⇒ thin held-out sets ⇒ wider CIs.
- Random-walk directional ties excluded (slightly fewer windows than other methods).
- CRPS is an even-grid quantile approximation.

---

## 12. References

Das et al. 2024 (TimesFM) · Fu, Hirano & Imajo 2024 (arXiv:2412.09880) · Hu et al.
2021 (LoRA) · Kim et al. 2021 (RevIN) · Hyndman & Koehler 2006 (MASE) · Gneiting &
Raftery 2007 (CRPS) · Diebold & Mariano 1995; Harvey et al. 1997 (DM) · McNemar 1947
· Künsch 1989; Politis & Romano 1994 (block/stationary bootstrap) · Benjamini &
Hochberg 1995 (FDR) · Matthews 1975 (MCC) · Brodersen et al. 2010 (balanced acc) ·
Lo 2002 (Sharpe statistics).
