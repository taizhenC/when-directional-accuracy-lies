"""Reproducibility + orchestration tests (CPU, no 200M model).

Covers seeding, the 3-state train_adapter return + adapter_meta resume, the
per-sector fail-loud coverage guard, the run_meta manifest, and the legacy date fix.
"""

import random
import types

import numpy as np
import pytest
import torch

from finetune.config import TrainingConfig
from finetune.splits import Fold
from finetune.trainer import seed_everything


def test_seed_everything_is_deterministic():
    seed_everything(123)
    a = (random.random(), float(np.random.rand()), int(torch.randint(0, 10**9, (1,)).item()))
    seed_everything(123)
    b = (random.random(), float(np.random.rand()), int(torch.randint(0, 10**9, (1,)).item()))
    assert a == b
    seed_everything(124)
    c = (random.random(), float(np.random.rand()), int(torch.randint(0, 10**9, (1,)).item()))
    assert a != c


def test_training_summary_status_shapes():
    from finetune.run_benchmark import _training_summary
    assert _training_summary(0, "pooled", "skipped_no_samples", None) == {
        "fold": 0, "adapter": "pooled", "status": "skipped_no_samples"}
    assert _training_summary(0, "tech", "reused_existing", None)["status"] == "reused_existing"
    s = _training_summary(1, "tech", "trained", {"best_epoch": 4, "n_epochs_run": 9,
                                                 "best_val_loss": 0.5,
                                                 "train_loss": [1.0, 0.3], "val_loss": [1.0, 0.4]})
    assert s["status"] == "trained" and s["best_epoch"] == 4 and s["final_val_loss"] == 0.4


def test_run_meta_required_keys_and_json():
    import json

    from finetune.run_benchmark import _run_meta
    m = _run_meta(TrainingConfig(), pooled_only=True, version="vX")
    for k in ("seed", "git_commit", "git_dirty", "pooled_only", "torch", "cuda",
              "gpu_name", "hyperparams", "pip_freeze"):
        assert k in m
    assert m["seed"] == 42 and m["pooled_only"] is True
    json.dumps(m)


def test_legacy_fold_scores_2024():
    # Fold.test_start == val_end, so val_end=2024 makes the legacy test window 2024->2026.
    f = Fold(index=0, data_start="2014-01-01", train_end="2023-01-01",
             val_end="2024-01-01", test_end="2026-01-01")
    assert f.test_start == "2024-01-01"


def _mock_training(monkeypatch):
    """Patch the model-touching parts of train_adapter so it runs CPU-only."""
    import finetune.model_setup as ms
    import finetune.run_benchmark as rb
    import finetune.trainer as tr
    monkeypatch.setattr(rb, "build_train_val", lambda *a, **k: ([0] * 8, [0] * 8))
    monkeypatch.setattr(ms, "load_timesfm", lambda: types.SimpleNamespace(model=object()))
    draws = []

    def fake_create(internal_model, rank=16, alpha=32, dropout=0.05):
        draws.append(int(torch.randint(0, 10**9, (1,)).item()))
        return object()

    monkeypatch.setattr(ms, "create_lora_model", fake_create)

    class DummyModel:
        def save_pretrained(self, path):
            import os
            os.makedirs(path, exist_ok=True)

    monkeypatch.setattr(tr, "fine_tune", lambda m, t, v, c: (
        DummyModel(), {"best_epoch": 1, "n_epochs_run": 1, "best_val_loss": 0.0,
                       "train_loss": [0.1], "val_loss": [0.2]}))
    return draws


def test_seed_before_lora_init_and_status(monkeypatch, tmp_path):
    import finetune.run_benchmark as rb
    draws = _mock_training(monkeypatch)
    cfg = TrainingConfig()
    fold = types.SimpleNamespace(index=0)
    s1, h1 = rb.train_adapter({}, fold, [], cfg, cfg.lora_rank, cfg.stride_default,
                              str(tmp_path / "pooled"), version="v")
    s2, h2 = rb.train_adapter({}, fold, [], cfg, cfg.lora_rank, cfg.stride_default,
                              str(tmp_path / "pooled2"), version="v")
    assert draws[0] == draws[1]                       # reproducible LoRA init (seed precedes create)
    assert s1 == "trained" and h1["best_epoch"] == 1 and h2["n_epochs_run"] == 1


def test_resume_reuses_only_on_meta_match(monkeypatch, tmp_path):
    import finetune.run_benchmark as rb
    _mock_training(monkeypatch)
    cfg = TrainingConfig()
    fold = types.SimpleNamespace(index=0)
    sp = str(tmp_path / "pooled")
    assert rb.train_adapter({}, fold, [], cfg, cfg.lora_rank, cfg.stride_default, sp,
                            version="v", resume=True)[0] == "trained"
    # identical identity -> reused
    assert rb.train_adapter({}, fold, [], cfg, cfg.lora_rank, cfg.stride_default, sp,
                            version="v", resume=True)[0] == "reused_existing"
    # rank mismatch -> retrain (never silently reuse a stale adapter)
    assert rb.train_adapter({}, fold, [], cfg, 999, cfg.stride_default, sp,
                            version="v", resume=True)[0] == "trained"
    # no training samples -> skipped
    monkeypatch.setattr(rb, "build_train_val", lambda *a, **k: ([], []))
    assert rb.train_adapter({}, fold, [], cfg, cfg.lora_rank, cfg.stride_default,
                            str(tmp_path / "p2"), version="v", resume=True)[0] == "skipped_no_samples"


def test_run_fold_fails_loud_on_missing_sector(monkeypatch):
    import finetune.run_benchmark as rb

    class DummyES:
        split, category, series_norm = "seen", "stock", None

    monkeypatch.setattr(rb, "prepare_eval_series", lambda *a, **k: [DummyES()])

    def fake_train(records, fold, tickers, config, rank, stride, save_path,
                   version=None, resume=False):
        import os
        if os.path.basename(save_path) == "pooled":
            return "trained", {"train_loss": [0.1], "val_loss": [0.2], "best_epoch": 1,
                               "n_epochs_run": 1, "best_val_loss": 0.2}
        return "skipped_no_samples", None            # every sector fails to train

    monkeypatch.setattr(rb, "train_adapter", fake_train)
    cfg = TrainingConfig()
    cfg.sectors, cfg.small_sectors = ["tech"], []
    holdout = types.SimpleNamespace(by_sector={"tech": {"seen": ["AAA"], "held_out": []}},
                                    seen_set=lambda: {"AAA"})
    fold = Fold(index=2, data_start="2005-01-01", train_end="2023-01-01",
                val_end="2024-01-01", test_end="2026-01-01")
    tmeta = {"AAA": {"sector": "tech", "category": "stock"}}
    # Full (non-smoke) run must FAIL LOUD: the registered per-sector test needs coverage.
    with pytest.raises(RuntimeError):
        rb.run_fold({}, tmeta, {}, fold, holdout, cfg, "v", smoke=False, pooled_only=False)
