"""Render the canonical paper tables (A-D) from a benchmark raw.json.

    python -m scripts.render_tables --version <frozen-version>
    # or: python -m scripts.render_tables --path results/benchmark/<v>/raw.json

Writes ``tables.md`` next to raw.json. Tables A/B/C are aggregated across folds
(mean of metrics, sum of counts); Table D is listed per fold with the
pre-registered primary test flagged and BH-FDR-adjusted p-values shown.

Pure stdlib + numpy, CPU — unit-tested in tests/test_render.py.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

import numpy as np


def _is_num(x):
    return isinstance(x, (int, float)) and not (isinstance(x, float) and x != x)


def _mean(vals):
    a = np.array([v for v in vals if _is_num(v)], dtype=float)
    return float(a.mean()) if a.size else float("nan")


def _fmt(x, p=4):
    if x is None:
        return ""
    if isinstance(x, float):
        return "" if x != x else f"{x:.{p}f}"
    if isinstance(x, (list, tuple)):
        return "[" + ", ".join(_fmt(v, p) for v in x) + "]"
    return str(x)


def aggregate(rows, keys, sum_fields=(), mean_fields=()):
    """Group rows by ``keys``; sum ``sum_fields``, mean ``mean_fields`` across folds."""
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r.get(k) for k in keys)].append(r)
    out = []
    for kv in sorted(groups, key=lambda t: [str(v) for v in t]):
        rs = groups[kv]
        row = dict(zip(keys, kv))
        for f in sum_fields:
            row[f] = int(np.nansum([rr.get(f) or 0 for rr in rs]))
        for f in mean_fields:
            row[f] = _mean([rr.get(f) for rr in rs])
        out.append(row)
    return out


def md_table(rows, columns, headers=None):
    headers = headers or columns
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(columns)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(_fmt(r.get(c)) for c in columns) + " |")
    return "\n".join(lines)


def render(payload) -> str:
    t = payload["tables"]
    parts = [f"# Benchmark tables — {payload.get('version', '')}",
             f"_smoke={payload.get('smoke')}_  ·  folds={len(payload.get('folds', []))}\n"]

    # Table A — directional / trading
    a = aggregate(
        t["A"], ["method", "split", "category", "horizon"],
        sum_fields=["n_windows", "n_trades"],
        mean_fields=["acc", "always_up_acc", "excess_acc", "balanced_acc", "mcc",
                     "sharpe", "sharpe_net", "max_drawdown", "hit_rate"])
    parts.append("## Table A — directional / trading (fold-mean)\n")
    parts.append(md_table(a, ["method", "split", "category", "horizon", "n_windows",
                              "n_trades", "acc", "always_up_acc", "excess_acc",
                              "balanced_acc", "mcc", "sharpe", "max_drawdown",
                              "hit_rate"]))

    # Table B — point forecast
    b = aggregate(
        t["B"], ["method", "split", "category"],
        sum_fields=["n", "n_windows"],
        mean_fields=["MAE", "RMSE", "sMAPE", "MASE"])
    parts.append("\n## Table B — point forecast (fold-mean, macro-averaged)\n")
    parts.append(md_table(b, ["method", "split", "category", "n_windows",
                              "MAE", "RMSE", "sMAPE", "MASE"]))

    # Table C — calibration
    c = aggregate(
        t["C"], ["method", "split", "category", "quantile_level"],
        mean_fields=["nominal", "empirical_coverage", "pinball"])
    parts.append("\n## Table C — calibration (fold-mean)\n")
    parts.append(md_table(c, ["method", "split", "category", "quantile_level",
                              "nominal", "empirical_coverage", "pinball"]))

    # Table D — significance (per fold; primary flagged)
    d = sorted(t["D"], key=lambda r: (not r.get("primary", False), r.get("split", ""),
                                      r.get("comparison", ""), r.get("horizon", 0)))
    parts.append("\n## Table D — significance (primary test flagged ★)\n")
    drows = [{**r, "comparison": ("★ " if r.get("primary") else "") + r.get("comparison", "")}
             for r in d]
    parts.append(md_table(drows, ["comparison", "split", "horizon", "test",
                                  "statistic", "p", "fdr_adjusted", "fdr_reject", "n"]))
    return "\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--version", default=None)
    ap.add_argument("--path", default=None, help="path to raw.json (overrides --version)")
    ap.add_argument("--root", default=os.path.join("results", "benchmark"))
    args = ap.parse_args()

    path = args.path
    if path is None:
        if args.version is None:
            versions = sorted(os.listdir(args.root))
            args.version = versions[-1]
        path = os.path.join(args.root, args.version, "raw.json")

    with open(path) as f:
        payload = json.load(f)
    md = render(payload)
    out = os.path.join(os.path.dirname(path), "tables.md")
    with open(out, "w") as f:
        f.write(md)
    print(f"[render] wrote {out}")


if __name__ == "__main__":
    main()
