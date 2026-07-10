"""Walk-forward benchmark orchestrator (Colab GPU entrypoint).

Per fold (train -> validation -> test):
  1. Build per-ticker TEST EvalSeries (eval normalizer fit on pre-target history).
  2. Train the pooled adapter (all seen stocks) and 11 per-sector adapters
     (each on its sector's seen stocks + SPDR ETF anchor), early-stopping on the
     VALIDATION window (never test).
  3. Evaluate zero-shot base, pooled, per-sector, and the 4 naive baselines over
     identical windows; score Tables A/B/C and the pairwise significance Table D.
  4. Aggregate across folds, BH-FDR the exploratory family, write
     results/benchmark/<version>/raw.json (+ headline markdown).

This module trains models -> it requires a GPU and is meant to run on Colab.
The pure-numpy pieces it depends on (metrics, baselines, windowing) are unit-
tested on CPU; use --smoke for a 1-sector / 1-fold / few-epoch end-to-end check.

Zero-shot isolation: a dedicated base instance serves the zero-shot baseline; the
adapters live on a separate base (PEFT named adapters). A torch.allclose check
confirms the zero-shot base is unaffected by adapter loading.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from collections import defaultdict

import numpy as np

from finetune import benchmark as B
from finetune.benchmark import (
    EvalSeries,
    MethodWindows,
    assemble,
    baseline_paths,
    directional_correct,
    model_paths,
    score_calibration,
    score_directional_trading,
    score_point,
    squared_error_at,
)
from finetune.config import TrainingConfig
from finetune.data_collector import SECTOR_TO_ETF
from finetune.data_frozen import load_frozen
from finetune.data_prep import LogNormalizer, TimeSeriesDataset
from finetune.metrics import benjamini_hochberg, diebold_mariano, mcnemar_test
from finetune.splits import Fold, holdout_split, values_between, walk_forward_folds

ADAPTER_ROOT = os.path.join("adapters", "walkforward")
RESULTS_ROOT = os.path.join("results", "benchmark")


# --------------------------------------------------------------------------- #
# Data preparation
# --------------------------------------------------------------------------- #
def prepare_eval_series(records_by_ticker, ticker_meta, fold, holdout, config,
                        tickers) -> list[EvalSeries]:
    """Build TEST EvalSeries for the given tickers (in the given order).

    Eval normalizer is fit on pre-target history [data_start, test_start) only.
    """
    out = []
    held = holdout.held_out_set()
    for ticker in tickers:
        series = records_by_ticker.get(ticker)
        if series is None:
            continue
        info = ticker_meta[ticker]
        pre = values_between(series, fold.data_start, fold.test_start)
        test = values_between(series, fold.test_start, fold.test_end)
        if len(pre) < config.context_len or len(test) < config.horizon:
            continue
        norm = LogNormalizer()
        norm.fit(pre, series_id=0)
        full = np.concatenate([pre[-config.context_len:], test])
        out.append(EvalSeries(
            ticker=ticker, sector=info["sector"], category=info["category"],
            split=("held_out" if ticker in held else "seen"),
            series_norm=norm.transform(full, 0), normalizer=norm, series_id=0,
            train_prices=values_between(series, fold.data_start, fold.train_end),
        ))
    return out


def build_train_val(records_by_ticker, fold, tickers, config, stride):
    """TimeSeriesDatasets for training (train slice) and early-stopping (val window).

    Training normalizer fit on the train slice only; the val series is the
    validation window prefixed with the train tail (for context).
    """
    train_series, val_series = [], []
    for sid, ticker in enumerate(tickers):
        series = records_by_ticker.get(ticker)
        if series is None:
            continue
        train_raw = values_between(series, fold.data_start, fold.train_end)
        val_raw = values_between(series, fold.train_end, fold.val_end)
        if len(train_raw) < config.min_series_len:
            continue
        norm = LogNormalizer()
        norm.fit(train_raw, series_id=sid)
        train_series.append(norm.transform(train_raw, series_id=sid))
        if len(val_raw) >= config.horizon:
            prefix = train_raw[-config.context_len:]
            val_series.append(norm.transform(np.concatenate([prefix, val_raw]), sid))

    train_ds = TimeSeriesDataset(train_series, config.context_len, config.horizon, stride)
    val_ds = TimeSeriesDataset(val_series, config.context_len, config.horizon, stride)
    return train_ds, val_ds


# --------------------------------------------------------------------------- #
# Training
# --------------------------------------------------------------------------- #
def _adapter_meta(version, fold, save_path, config, rank):
    """Identity of an adapter, for resume verification (adapter_meta.json)."""
    commit, dirty = _git_state()
    return {
        "version": version,
        "fold": fold.index,
        "adapter": os.path.basename(os.path.normpath(save_path)),
        "seed": getattr(config, "seed", 42),
        "rank": rank,
        "alpha": config.lora_alpha,
        "dropout": config.lora_dropout,
        "git_commit": commit,
        "git_dirty": dirty,
    }


def train_adapter(records_by_ticker, fold, tickers, config, rank, stride, save_path,
                  version=None, resume=False):
    """Train one LoRA adapter (early-stop on validation) and save it.

    Returns ``(status, history)`` where status is one of:
      * ``"trained"``            — freshly trained (history is the curves dict)
      * ``"reused_existing"``    — resume hit a matching adapter_meta (history None)
      * ``"skipped_no_samples"`` — no training windows (history None)
    """
    from finetune.model_setup import create_lora_model, load_timesfm
    from finetune.trainer import fine_tune, seed_everything

    want = _adapter_meta(version, fold, save_path, config, rank)
    meta_path = os.path.join(save_path, "adapter_meta.json")
    # Resume only on an EXACT identity match — never silently reuse a stale adapter.
    if resume and os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                have = json.load(f)
        except Exception:
            have = None
        if have == want:
            print(f"  [train] REUSE {save_path} (adapter_meta matches)")
            return "reused_existing", None
        print(f"  [train] RETRAIN {save_path}: adapter_meta mismatch")

    train_ds, val_ds = build_train_val(records_by_ticker, fold, tickers, config, stride)
    if len(train_ds) == 0:
        print(f"  [train] SKIP {save_path}: no training samples")
        return "skipped_no_samples", None

    cfg = copy.copy(config)
    cfg.lora_rank = rank
    # fine_tune() checkpoints best-val weights to save_dir/<asset_class>_best;
    # derive both from save_path so the per-adapter checkpoint is unique and the
    # shared TrainingConfig is untouched (mirrors finetune/main.py).
    cfg.asset_class = os.path.basename(os.path.normpath(save_path))
    cfg.save_dir = os.path.dirname(os.path.normpath(save_path)) or "."
    # Seed BEFORE LoRA init: create_lora_model()/get_peft_model() draw the random
    # A-matrix from the global torch RNG, so the seed must be set here, not only
    # inside fine_tune() (fine_tune reseeds again for the training stochasticity).
    seed_everything(cfg.seed)
    base = load_timesfm()
    lora = create_lora_model(base.model, rank=rank, alpha=config.lora_alpha,
                             dropout=config.lora_dropout)
    trained, history = fine_tune(lora, train_ds, val_ds, cfg)
    os.makedirs(save_path, exist_ok=True)
    trained.save_pretrained(save_path)
    with open(meta_path, "w") as f:
        json.dump(want, f, indent=2, default=lambda o: None)
    print(f"  [train] saved {save_path} (train={len(train_ds)} val={len(val_ds)})")

    del base, lora, trained
    _empty_cache()
    return "trained", history


def _empty_cache():
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass


# --------------------------------------------------------------------------- #
# Evaluation helpers
# --------------------------------------------------------------------------- #
def _device():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def filter_mw(mw: MethodWindows, eval_all, split=None, category=None) -> MethodWindows:
    """Subset windows whose source EvalSeries matches split/category."""
    if mw.n == 0:
        return mw
    keep = np.array([
        (split is None or eval_all[t].split == split)
        and (category is None or eval_all[t].category == category)
        for t in mw.ticker_id
    ])
    q = mw.quantile_price[keep] if mw.quantile_price is not None else None
    return MethodWindows(
        ticker_id=mw.ticker_id[keep], current_norm=mw.current_norm[keep],
        future_norm=mw.future_norm[keep], pred_norm=mw.pred_norm[keep],
        current_price=mw.current_price[keep], future_price=mw.future_price[keep],
        pred_price=mw.pred_price[keep], quantile_price=q,
        per_ticker_scale=mw.per_ticker_scale,
    )


def score_method_rows(mw, eval_all, method, fold_idx, cost_bps):
    """Table A/B/C rows for a method across split x category cells."""
    rows_a, rows_b, rows_c = [], [], []
    for split in ("seen", "held_out"):
        for category in ("stock", "etf"):
            cell = filter_mw(mw, eval_all, split, category)
            if cell.n == 0:
                continue
            tag = {"method": method, "fold": fold_idx, "split": split,
                   "category": category}
            for r in score_directional_trading(cell, cost_bps=cost_bps):
                rows_a.append({**tag, **r})
            if method not in B.POINT_EXCLUDE:   # skip divergent level forecasts
                rows_b.append({**tag, **score_point(cell)})
            cal, crps = score_calibration(cell)
            if cal is not None:
                for r in cal:
                    rows_c.append({**tag, "crps": crps, **r})
    return rows_a, rows_b, rows_c


# --------------------------------------------------------------------------- #
# One fold
# --------------------------------------------------------------------------- #
def run_fold(records_by_ticker, ticker_meta, meta, fold, holdout, config,
             version, smoke, pooled_only=False, run_tag=None, resume=False,
             smoke_sectors=None):
    from peft import PeftModel

    from finetune.model_setup import load_timesfm

    # run_tag isolates BOTH results and adapters: a smoke run (run_tag="smoke") writes
    # adapters under <version>__smoke so it can never collide with / be resume-reused
    # by the full run.
    vtag = version + (f"__{run_tag}" if run_tag else "")
    fold_dir = os.path.join(ADAPTER_ROOT, vtag, f"fold_{fold.index}")

    if pooled_only:
        # Pooled-only: a single ordered eval list over all stocks + anchor ETF(s),
        # no per-sector adapters. Pooled trains on seen stocks and is scored on
        # seen + held_out, identically to the full benchmark's pooled method.
        sectors, sector_slices = [], {}
        stocks = sorted(t for t, i in ticker_meta.items() if i["category"] == "stock")
        etfs = sorted(t for t, i in ticker_meta.items() if i["category"] == "etf")
        eval_all = prepare_eval_series(records_by_ticker, ticker_meta, fold, holdout,
                                       config, stocks + etfs)
    else:
        # smoke trains 1 sector by default (fast gate); smoke_sectors="all" exercises
        # the full multi-sector path at low epochs (the per-sector dry run).
        sectors = (config.sectors[:1] if (smoke and smoke_sectors != "all")
                   else config.sectors)
        # Ordered eval list: sector by sector (stocks + ETF), so per-sector concat
        # stays row-aligned with pooled / zero-shot.
        by_sector_tickers = defaultdict(list)
        for t, info in ticker_meta.items():
            if info["sector"] in sectors:
                by_sector_tickers[info["sector"]].append(t)
        eval_all, sector_slices = [], {}
        for sec in sectors:
            ordered = sorted(by_sector_tickers[sec])      # stocks + the ETF
            es = prepare_eval_series(records_by_ticker, ticker_meta, fold, holdout,
                                     config, ordered)
            sector_slices[sec] = (len(eval_all), len(eval_all) + len(es))
            eval_all.extend(es)

    if not eval_all:
        print(f"[fold {fold.index}] no eval series; skipping")
        return None

    seen_stocks = sorted(holdout.seen_set())

    # ---- TRAIN ----
    label = "pooled only" if pooled_only else f"pooled + {len(sectors)} sector adapters"
    print(f"[fold {fold.index}] training {label}")
    training = []   # per-adapter status + best_epoch summaries for run_meta
    pooled_dir = os.path.join(fold_dir, "pooled")
    status, hist = train_adapter(records_by_ticker, fold, seen_stocks, config,
                                 config.lora_rank, config.stride_default, pooled_dir,
                                 version=version, resume=resume)
    training.append(_training_summary(fold.index, "pooled", status, hist))
    if status not in ("trained", "reused_existing"):
        raise RuntimeError(f"[fold {fold.index}] pooled adapter not trained "
                           f"(status={status}); cannot evaluate.")
    trained_sectors = []                         # sectors with a usable adapter
    for sec in sectors:
        sec_seen = sorted(holdout.by_sector.get(sec, {}).get("seen", []))
        train_tickers = sec_seen + ([SECTOR_TO_ETF[sec]] if sec in SECTOR_TO_ETF else [])
        is_small = sec in config.small_sectors
        rank = config.lora_rank_small_sector if is_small else config.lora_rank
        stride = config.stride_small_sector if is_small else config.stride_default
        status, hist = train_adapter(records_by_ticker, fold, train_tickers, config,
                                     rank, stride, os.path.join(fold_dir, sec),
                                     version=version, resume=resume)
        training.append(_training_summary(fold.index, sec, status, hist))
        if status in ("trained", "reused_existing"):
            trained_sectors.append(sec)
        else:
            print(f"  [fold {fold.index}] sector {sec} not covered (status={status})")
    # Fail loud on a full run: the registered per-sector test needs all 11 sectors.
    missing = [s for s in sectors if s not in trained_sectors]
    if missing and not smoke:
        raise RuntimeError(
            f"[fold {fold.index}] sectors with no adapter: {missing}. The registered "
            "per-sector test requires complete coverage — failing loudly.")

    # ---- EVAL ----
    device = _device()
    base_zs = load_timesfm().model.to(device)        # dedicated zero-shot base
    eval_base = load_timesfm().model.to(device)      # carries adapters

    # zero-shot isolation probe (before adapters are attached)
    probe = np.asarray([eval_all[0].series_norm[:config.context_len]], dtype=float)
    zs_probe_before, _ = model_paths(base_zs, probe, config.horizon)

    peft = PeftModel.from_pretrained(eval_base, pooled_dir, adapter_name="pooled").to(device)
    for sec in trained_sectors:
        peft.load_adapter(os.path.join(fold_dir, sec), adapter_name=sec)

    zs_probe_after, _ = model_paths(base_zs, probe, config.horizon)
    import torch
    assert torch.allclose(torch.tensor(zs_probe_before), torch.tensor(zs_probe_after),
                          atol=1e-5), "zero-shot base mutated by adapter loading"

    def model_predict(m):
        return lambda c: model_paths(m, c, config.horizon)

    methods = {}
    methods["zero_shot"] = assemble(eval_all, model_predict(base_zs),
                                    config.horizon, with_quantiles=True)
    peft.set_adapter("pooled")
    methods["pooled"] = assemble(eval_all, model_predict(peft), config.horizon,
                                 with_quantiles=True)
    # per-sector: evaluate each covered sector's slice with its adapter, then concat
    # in order. If only some sectors are covered (smoke), per_sector spans fewer rows
    # than pooled and the DM guard (f[a].n == f[b].n) skips that comparison safely.
    if not pooled_only and trained_sectors:
        sector_parts = []
        for sec in trained_sectors:
            lo, hi = sector_slices[sec]
            peft.set_adapter(sec)
            sector_parts.append(assemble(eval_all[lo:hi], model_predict(peft),
                                         config.horizon, with_quantiles=True))
        methods["per_sector"] = MethodWindows.concat(sector_parts)
    for name in B.BASELINES:
        methods[name] = assemble(eval_all, (lambda nm: lambda c: baseline_paths(nm, c))(name),
                                 config.horizon, with_quantiles=False)

    # ---- SCORE ----
    rows_a, rows_b, rows_c = [], [], []
    for name, mw in methods.items():
        a, b, c = score_method_rows(mw, eval_all, name, fold.index, config_cost(config))
        rows_a += a; rows_b += b; rows_c += c

    rows_d = fold_significance(methods, eval_all, fold.index)

    del base_zs, eval_base, peft
    _empty_cache()
    return {"A": rows_a, "B": rows_b, "C": rows_c, "D": rows_d, "training": training}


def config_cost(config):
    return getattr(config, "cost_bps", 0.0)


# --------------------------------------------------------------------------- #
# Significance (Table D)
# --------------------------------------------------------------------------- #
def fold_significance(methods, eval_all, fold_idx, horizons=B.HORIZONS):
    rows = []
    dm_pairs = [("per_sector", "pooled"), ("pooled", "zero_shot"),
                ("per_sector", "zero_shot")]
    for split in ("seen", "held_out"):
        f = {m: filter_mw(mw, eval_all, split, "stock") for m, mw in methods.items()}
        for h in horizons:
            for a, b in dm_pairs:
                if a not in f or b not in f:
                    continue
                if f[a].n > 1 and f[a].n == f[b].n:
                    dm = diebold_mariano(squared_error_at(f[a], h),
                                         squared_error_at(f[b], h), horizon=h)
                    rows.append({"comparison": f"{a} vs {b}", "fold": fold_idx,
                                 "split": split, "category": "stock", "horizon": h,
                                 "test": "diebold_mariano", "statistic": dm["statistic"],
                                 "p": dm["p"], "n": dm["n"]})
            for m in ("pooled", "per_sector"):
                if m not in f or f[m].n == 0 or f["always_up"].n != f[m].n:
                    continue
                mok, _ = directional_correct(f[m], h)
                aok, _ = directional_correct(f["always_up"], h)
                mc = mcnemar_test(mok, aok)
                rows.append({"comparison": f"{m} vs always_up", "fold": fold_idx,
                             "split": split, "category": "stock", "horizon": h,
                             "test": "mcnemar", "statistic": mc["statistic"],
                             "p": mc["p"], "n": mc["n_discordant"]})
    return rows


def mark_primary_and_fdr(rows_d):
    """Flag the pre-registered primary test and BH-FDR the exploratory family."""
    def is_primary(r):
        return (r["comparison"] == "per_sector vs pooled" and r["split"] == "held_out"
                and r["category"] == "stock" and r["horizon"] == 128
                and r["test"] == "diebold_mariano")

    secondary_idx = [i for i, r in enumerate(rows_d) if not is_primary(r)]
    pvals = [rows_d[i]["p"] for i in secondary_idx]
    q, reject = benjamini_hochberg(pvals)
    for j, i in enumerate(secondary_idx):
        rows_d[i]["primary"] = False
        rows_d[i]["fdr_adjusted"] = float(q[j]) if q[j] == q[j] else None
        rows_d[i]["fdr_reject"] = bool(reject[j])
    for i, r in enumerate(rows_d):
        if is_primary(r):
            r["primary"] = True
            r["fdr_adjusted"] = None
    return rows_d


# --------------------------------------------------------------------------- #
# Reproducibility manifest
# --------------------------------------------------------------------------- #
def _git(args):
    import subprocess
    try:
        return subprocess.check_output(
            ["git"] + args, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def _git_state():
    """(commit, dirty) over TRACKED files only — untracked run outputs don't count."""
    commit = _git(["rev-parse", "HEAD"])
    status = _git(["status", "--porcelain", "--untracked-files=no"])
    return commit, (bool(status.strip()) if status is not None else None)


def _training_summary(fold_idx, name, status, hist):
    """Compact per-adapter training record for the reproducibility manifest.

    ``status`` is one of trained / reused_existing / skipped_no_samples.
    """
    base = {"fold": fold_idx, "adapter": name, "status": status}
    if hist is None:
        return base
    tl, vl = hist.get("train_loss") or [], hist.get("val_loss") or []
    return {**base,
            "best_epoch": hist.get("best_epoch"),
            "n_epochs_run": hist.get("n_epochs_run"),
            "best_val_loss": hist.get("best_val_loss"),
            "final_train_loss": (tl[-1] if tl else None),
            "final_val_loss": (vl[-1] if vl else None)}


def _run_meta(config, pooled_only, version):
    """Reproducibility manifest: seed, git state, env, and hyperparameters.

    ``git_dirty`` matters: "byte-identical code" is only defensible if the tree
    was clean at run time. All lookups degrade to None rather than raising.
    """
    import platform
    import subprocess
    import sys

    commit, dirty = _git_state()
    try:
        import torch
        torch_v, cuda_v = torch.__version__, torch.version.cuda
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception:
        torch_v = cuda_v = gpu = None
    try:
        freeze = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"],
            stderr=subprocess.DEVNULL).decode().splitlines()
    except Exception:
        freeze = None

    return {
        "version": version,
        "seed": getattr(config, "seed", 42),
        "pooled_only": pooled_only,
        "git_commit": commit,
        "git_dirty": dirty,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": torch_v, "cuda": cuda_v, "gpu_name": gpu,
        "hyperparams": {
            "lora_rank": config.lora_rank, "lora_alpha": config.lora_alpha,
            "lora_dropout": config.lora_dropout, "batch_size": config.batch_size,
            "lr": config.lr, "weight_decay": config.weight_decay,
            "epochs": config.epochs, "patience": config.patience,
            "min_epochs": config.min_epochs, "context_len": config.context_len,
            "horizon": config.horizon, "loss_type": config.loss_type,
            "direction_weight": config.direction_weight,
        },
        "pip_freeze": freeze,
    }


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run(version=None, smoke=False, n_folds=3, epochs=None, out_root=RESULTS_ROOT,
        pooled_only=False, run_tag=None, resume=False, smoke_sectors=None):
    config = TrainingConfig()
    if epochs is not None:
        config.epochs = epochs
        config.min_epochs = min(config.min_epochs, epochs)

    records, meta = load_frozen(version)
    version = meta["version"]
    records_by_ticker = dict(records)
    ticker_meta = meta["tickers"]

    from finetune.data_frozen import ticker_to_sector
    holdout = holdout_split(ticker_to_sector(meta, category="stock"), seed=42)

    folds = walk_forward_folds(n_folds=n_folds)
    if smoke:
        folds = folds[-1:]

    all_rows = {"A": [], "B": [], "C": [], "D": [], "training": []}
    for fold in folds:
        res = run_fold(records_by_ticker, ticker_meta, meta, fold, holdout,
                       config, version, smoke, pooled_only=pooled_only,
                       run_tag=run_tag, resume=resume, smoke_sectors=smoke_sectors)
        if res is None:
            continue
        for k in all_rows:
            all_rows[k] += res[k]

    all_rows["D"] = mark_primary_and_fdr(all_rows["D"])
    training = all_rows.pop("training")           # keep tables = {A,B,C,D}

    run_meta = _run_meta(config, pooled_only, version)
    run_meta["training"] = training

    out_dir = os.path.join(out_root, version + (f"__{run_tag}" if run_tag else ""))
    os.makedirs(out_dir, exist_ok=True)
    payload = {"version": version, "smoke": smoke, "pooled_only": pooled_only,
               "folds": [f.to_dict() for f in folds],
               "holdout": holdout.to_dict(), "tables": all_rows,
               "training": training, "run_meta": run_meta}
    with open(os.path.join(out_dir, "raw.json"), "w") as f:
        json.dump(payload, f, indent=2, default=lambda o: None)
    with open(os.path.join(out_dir, "run_meta.json"), "w") as f:
        json.dump(run_meta, f, indent=2, default=lambda o: None)
    print(f"[done] wrote {os.path.join(out_dir, 'raw.json')} "
          f"(A={len(all_rows['A'])} B={len(all_rows['B'])} "
          f"C={len(all_rows['C'])} D={len(all_rows['D'])} rows; "
          f"seed={run_meta['seed']} commit={run_meta['git_commit']} "
          f"dirty={run_meta['git_dirty']})")
    return payload


# --------------------------------------------------------------------------- #
# Legacy reproduce-and-debunk of the original ~80%
# --------------------------------------------------------------------------- #
def legacy_raw_eval(version=None, data_start="2014-01-01", train_end="2023-01-01",
                    val_end="2024-01-01", test_end="2026-01-01",
                    out_root=os.path.join("results", "legacy"), epochs=None,
                    run_tag="legacy", resume=True):
    """Recreate the OLD ~80% condition and debunk it in one shot.

    Trains a pooled adapter on a 2014+ bull window and scores RAW directional
    accuracy on the 2024->2026 test window, alongside ``always_up_acc`` and
    ``excess_acc`` so the base-rate artifact is explicit. Honest early-stopping on
    2023->2024 (no test-window leak). NOTE: ``Fold.test_start == val_end``
    (splits.py), so ``val_end='2024-01-01'`` makes the scored window 2024->2026.

    This recreates the *condition* under which raw accuracy approaches ~80%; it does
    not promise to bit-reproduce the original 0.778 (code/hyperparameters changed).
    Writes raw.json + run_meta.json under out_root and returns the payload.
    """
    from peft import PeftModel

    from finetune.data_frozen import ticker_to_sector
    from finetune.model_setup import load_timesfm

    config = TrainingConfig()
    if epochs is not None:
        config.epochs = epochs
        config.min_epochs = min(config.min_epochs, epochs)

    records, meta = load_frozen(version)
    version = meta["version"]
    records_by_ticker = dict(records)
    ticker_meta = meta["tickers"]
    holdout = holdout_split(ticker_to_sector(meta, category="stock"), seed=42)
    stocks = sorted(t for t, i in ticker_meta.items() if i["category"] == "stock")

    fold = Fold(index=0, data_start=data_start, train_end=train_end,
                val_end=val_end, test_end=test_end)

    vtag = version + (f"__{run_tag}" if run_tag else "")
    save_path = os.path.join(ADAPTER_ROOT, vtag, "fold_0", "pooled")
    print(f"[legacy] train pooled on {len(stocks)} stocks "
          f"[{data_start}->{train_end}], early-stop [{train_end}->{val_end}], "
          f"score [{val_end}->{test_end}]")
    status, hist = train_adapter(records_by_ticker, fold, stocks, config,
                                 config.lora_rank, config.stride_default, save_path,
                                 version=version, resume=resume)
    if status == "skipped_no_samples":
        raise RuntimeError("legacy_raw_eval: no training samples in the 2014+ window")

    eval_all = prepare_eval_series(records_by_ticker, ticker_meta, fold, holdout,
                                   config, stocks)
    device = _device()
    eval_base = load_timesfm().model.to(device)
    peft = PeftModel.from_pretrained(eval_base, save_path, adapter_name="pooled").to(device)
    peft.set_adapter("pooled")
    # model_paths returns (mean, quant) -> with_quantiles=True so assemble unpacks it
    # (baselines, which return just a path, use with_quantiles=False).
    mw = assemble(eval_all, lambda c: model_paths(peft, c, config.horizon),
                  config.horizon, with_quantiles=True)

    rows = []
    for split in ("seen", "held_out"):
        cell = filter_mw(mw, eval_all, split, "stock")
        if cell.n == 0:
            continue
        for r in score_directional_trading(cell):
            rows.append({"method": "legacy_pooled_2014", "split": split,
                         "category": "stock", **r})

    run_meta = _run_meta(config, True, version)
    run_meta["legacy_window"] = {"data_start": data_start, "train_end": train_end,
                                 "val_end": val_end, "test_end": test_end,
                                 "pooled_status": status,
                                 "best_epoch": (hist or {}).get("best_epoch")}
    out_dir = os.path.join(out_root, f"{version}_legacy_2014_2026")
    os.makedirs(out_dir, exist_ok=True)
    payload = {"version": version, "mode": "legacy_raw_eval",
               "window": run_meta["legacy_window"],
               "tables": {"A": rows}, "run_meta": run_meta}
    with open(os.path.join(out_dir, "raw.json"), "w") as f:
        json.dump(payload, f, indent=2, default=lambda o: None)
    with open(os.path.join(out_dir, "run_meta.json"), "w") as f:
        json.dump(run_meta, f, indent=2, default=lambda o: None)
    print(f"[legacy] wrote {os.path.join(out_dir, 'raw.json')} — raw accuracy recreates "
          f"the old ~80% condition; excess_acc shows it is the base rate.")
    for r in rows:
        if r["horizon"] in (2, 32, 64, 128):
            print(f"  {r['split']:8s} h={r['horizon']:3d}  acc={r['acc']:.3f}  "
                  f"always_up={r['always_up_acc']:.3f}  excess={r['excess_acc']:+.3f}")
    del eval_base, peft
    _empty_cache()
    return payload


def train_deployable(version=None, out_dir=os.path.join("adapters", "trained"),
                     sectors=None, epochs=None, data_start="2005-01-01",
                     train_end="2024-01-01", val_end="2026-01-01"):
    """Train DEPLOYABLE adapters on the full frozen data (no walk-forward).

    This is the "train my model" path (vs ``run()`` which is the walk-forward
    *benchmark*). Trains a pooled adapter (all stocks) + one per sector (sector
    stocks + SPDR ETF) on [data_start, train_end), early-stopping on the
    [train_end, val_end) validation window, and saves each to out_dir/<name>/.
    """
    config = TrainingConfig()
    if epochs is not None:
        config.epochs = epochs
        config.min_epochs = min(config.min_epochs, epochs)
    records, meta = load_frozen(version)
    records_by_ticker = dict(records)
    ticker_meta = meta["tickers"]
    sectors = sectors if sectors is not None else config.sectors

    fold = Fold(index=0, data_start=data_start, train_end=train_end,
                val_end=val_end, test_end=val_end)

    stocks = sorted(t for t, i in ticker_meta.items() if i["category"] == "stock")
    print(f"[train] pooled adapter on {len(stocks)} stocks")
    train_adapter(records_by_ticker, fold, stocks, config, config.lora_rank,
                  config.stride_default, os.path.join(out_dir, "pooled"),
                  version=meta["version"])

    for sec in sectors:
        sec_stocks = sorted(t for t, i in ticker_meta.items()
                            if i["category"] == "stock" and i["sector"] == sec)
        tickers = sec_stocks + ([SECTOR_TO_ETF[sec]] if sec in SECTOR_TO_ETF else [])
        is_small = sec in config.small_sectors
        rank = config.lora_rank_small_sector if is_small else config.lora_rank
        stride = config.stride_small_sector if is_small else config.stride_default
        print(f"[train] sector {sec}: {len(sec_stocks)} stocks + ETF (rank {rank})")
        train_adapter(records_by_ticker, fold, tickers, config, rank, stride,
                      os.path.join(out_dir, sec), version=meta["version"])
    print(f"[train] done -> {out_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["benchmark", "train"], default="benchmark",
                    help="benchmark = walk-forward eval; train = deployable adapters")
    ap.add_argument("--version", default=None, help="frozen-data version (default: latest)")
    ap.add_argument("--smoke", action="store_true", help="1 fold, 1 sector, few epochs")
    ap.add_argument("--folds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--sectors", nargs="*", default=None, help="subset of sectors")
    ap.add_argument("--pooled-only", action="store_true",
                    help="train/evaluate only the pooled adapter (no per-sector)")
    args = ap.parse_args()
    if args.mode == "train":
        train_deployable(version=args.version, sectors=args.sectors,
                         epochs=args.epochs)
    else:
        run(version=args.version, smoke=args.smoke, n_folds=args.folds,
            epochs=args.epochs if args.epochs else (2 if args.smoke else None),
            pooled_only=args.pooled_only)


if __name__ == "__main__":
    main()
