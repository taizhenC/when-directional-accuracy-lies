"""Generate paper figures from benchmark raw.json file(s). Read-only, no model.

Usage:
  python -m scripts.make_figures --out paper/figures \
      "NASDAQ-100=results/benchmark/<nasdaq_v>/raw.json" \
      "S&P 500=results/benchmark/<sp_v>/raw.json"

Each positional arg is LABEL=path; pass one or two universes. Figures (held-out
stocks, the generalization split):
  fig_excess_acc.png         excess directional accuracy vs horizon, pooled &
                             zero-shot, against the always-up=0 skill line
                             (THE headline: skill <= 0 at long horizons)
  fig_accuracy_vs_baserate.png  raw accuracy vs the always-up base rate by horizon
                             (the artifact: high accuracy, ~zero excess)
  fig_calibration.png        quantile reliability diagram (pooled vs zero-shot)
  fig_point_mae.png          MAE by horizon-agnostic point table (pooled vs
                             zero-shot vs always-up)

Error bars are +/- 1 SD across the walk-forward folds (per-fold block-bootstrap
CIs are also in raw.json if a tighter interval is wanted later).
"""

import argparse
import json
import os
from collections import defaultdict

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HORIZONS = [2, 4, 8, 16, 32, 64, 128]
_COLORS = plt.cm.tab10.colors


def _load(path):
    with open(path) as f:
        return json.load(f)


def _fold_stats(rows, method, field, split="held_out", category="stock", by="horizon"):
    """{key: (mean, std)} across folds for one method/split/category metric."""
    buckets = defaultdict(list)
    for r in rows:
        if (r.get("method") == method and r.get("split") == split
                and r.get("category") == category and r.get(field) is not None):
            buckets[r[by]].append(r[field])
    return {k: (float(np.mean(v)), float(np.std(v))) for k, v in buckets.items()}


def fig_excess_acc(universes, out):
    """Headline figure: excess accuracy (skill over always-up) vs horizon."""
    plt.figure(figsize=(7.2, 4.6))
    plt.axhline(0, color="black", lw=1.2, ls="--",
                label="always-up parity (zero skill)")
    for i, (label, d) in enumerate(universes.items()):
        A = d["tables"]["A"]
        for method, style, alpha in (("pooled", "-", 0.95),
                                     ("per_sector", "--", 0.8),
                                     ("zero_shot", ":", 0.5)):
            st = _fold_stats(A, method, "excess_acc")
            xs = [h for h in HORIZONS if h in st]
            if not xs:                       # per_sector only exists for the S&P run
                continue
            ys = [st[h][0] for h in xs]
            es = [st[h][1] for h in xs]
            plt.errorbar(xs, ys, yerr=es, marker="o", ls=style, capsize=3,
                         color=_COLORS[i], alpha=alpha,
                         label=f"{label} — {method}")
    plt.xscale("log", base=2)
    plt.xticks(HORIZONS, [str(h) for h in HORIZONS])
    plt.xlabel("forecast horizon h (trading days)")
    plt.ylabel("excess accuracy  (model − always-up)")
    plt.title("Directional skill over the base rate — held-out stocks")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    return _save(out, "fig-excess-acc.png")


def fig_accuracy_vs_baserate(universes, out):
    """The artifact: raw accuracy tracks the always-up base rate (high, no edge)."""
    n = len(universes)
    fig, axes = plt.subplots(1, n, figsize=(4.6 * n, 4.2), squeeze=False)
    for ax, (label, d) in zip(axes[0], universes.items()):
        A = d["tables"]["A"]
        au = _fold_stats(A, "always_up", "acc")
        po = _fold_stats(A, "pooled", "acc")
        xs = [h for h in HORIZONS if h in au and h in po]
        x = np.arange(len(xs))
        ax.bar(x - 0.2, [au[h][0] for h in xs], 0.4, label="always-up (base rate)",
               color="#bbbbbb")
        ax.bar(x + 0.2, [po[h][0] for h in xs], 0.4,
               yerr=[po[h][1] for h in xs], capsize=2, label="pooled LoRA",
               color=_COLORS[0])
        ax.axhline(0.5, color="black", lw=0.8, ls="--")
        ax.set_xticks(x)
        ax.set_xticklabels([str(h) for h in xs])
        ax.set_xlabel("horizon h")
        ax.set_ylabel("directional accuracy")
        ax.set_title(f"{label} — held-out stocks")
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    return _save(out, "fig-accuracy-vs-baserate.png")


def fig_calibration(universes, out):
    """Quantile reliability: empirical coverage vs nominal (pooled & zero-shot)."""
    n = len(universes)
    fig, axes = plt.subplots(1, n, figsize=(4.4 * n, 4.2), squeeze=False)
    for ax, (label, d) in zip(axes[0], universes.items()):
        C = d["tables"]["C"]
        ax.plot([0, 1], [0, 1], color="black", lw=1, ls="--", label="perfect")
        for j, method in enumerate(("pooled", "zero_shot")):
            pts = defaultdict(list)
            for r in C:
                if (r.get("method") == method and r.get("split") == "held_out"
                        and r.get("category") == "stock"):
                    pts[r["nominal"]].append(r["empirical_coverage"])
            xs = sorted(pts)
            ys = [float(np.mean(pts[x])) for x in xs]
            ax.plot(xs, ys, marker="o", color=_COLORS[j], label=method)
        ax.set_xlabel("nominal quantile level")
        ax.set_ylabel("empirical coverage")
        ax.set_title(f"{label} — calibration (held-out)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    plt.tight_layout()
    return _save(out, "fig-calibration.png")


def fig_point_mae(universes, out):
    """Point-forecast MAE (held-out stocks): pooled vs zero-shot vs always-up."""
    methods = ["always_up", "zero_shot", "pooled"]
    labels = list(universes)
    x = np.arange(len(labels))
    w = 0.25
    plt.figure(figsize=(1.8 * len(labels) + 2, 4.2))
    for j, m in enumerate(methods):
        vals = []
        for d in universes.values():
            B = d["tables"]["B"]
            v = [r["MAE"] for r in B if r.get("method") == m
                 and r.get("split") == "held_out" and r.get("category") == "stock"
                 and r.get("MAE") is not None]
            vals.append(float(np.mean(v)) if v else np.nan)
        plt.bar(x + (j - 1) * w, vals, w, label=m, color=_COLORS[j])
    plt.xticks(x, labels)
    plt.ylabel("MAE (price space, macro-averaged)")
    plt.title("Point-forecast error — held-out stocks (lower is better)")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    return _save(out, "fig-point-mae.png")


def _save(out, name):
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("universes", nargs="+", help="LABEL=path/to/raw.json (one or two)")
    ap.add_argument("--out", default="paper/figures", help="output directory")
    args = ap.parse_args()

    universes = {}
    for spec in args.universes:
        if "=" not in spec:
            raise SystemExit(f"expected LABEL=path, got: {spec}")
        label, path = spec.split("=", 1)
        universes[label] = _load(path)

    made = [
        fig_excess_acc(universes, args.out),
        fig_accuracy_vs_baserate(universes, args.out),
        fig_calibration(universes, args.out),
        fig_point_mae(universes, args.out),
    ]
    for p in made:
        print("wrote", p)


if __name__ == "__main__":
    main()
