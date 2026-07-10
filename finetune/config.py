"""Training configuration — single source of truth for all hyperparameters."""

from dataclasses import dataclass, field


@dataclass
class TrainingConfig:
    # Model
    base_model: str = "google/timesfm-2.5-200m-pytorch"
    lora_rank: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.05

    # Data
    context_len: int = 512
    horizon: int = 128
    random_context_mask: bool = True
    min_context: int = 128
    min_series_len: int = 252

    # Training
    epochs: int = 80
    batch_size: int = 512
    lr: float = 1e-4
    weight_decay: float = 0.01
    grad_clip: float = 1.0
    patience: int = 15
    min_epochs: int = 30       # don't allow early stopping before this epoch
    direction_weight: float = 0.3
    loss_type: str = "mse"
    seed: int = 42             # global RNG seed for reproducible training

    # Data window
    data_start: str = "2014-01-01"
    train_end: str = "2024-01-01"
    val_end: str = "2026-01-01"
    stride_default: int = 64
    stride_forex: int = 32

    # Per-sector uses longer history (captures 2008 crisis, more regimes)
    sector_data_start: str = "2005-01-01"

    # Per-class adapters
    asset_classes: list = field(
        default_factory=lambda: ["equity", "forex", "macro"]
    )

    # Per-sector adapters (see doc/PLAN_LORA_PER_SECTOR.md)
    # "asset_class" -> existing 3-adapter pipeline (equity / forex / macro)
    # "sector"      -> 11-adapter pipeline over GICS sectors of the S&P 500
    mode: str = "asset_class"
    sectors: list = field(
        default_factory=lambda: [
            "tech", "financials", "healthcare", "cons_disc", "industrials",
            "comms", "cons_staples", "energy", "utilities", "real_estate",
            "materials",
        ]
    )
    # Small sectors (<~30 names) get tighter stride + lower rank to combat
    # both data thinness and the overfit risk that comes with it.
    small_sectors: list = field(
        default_factory=lambda: [
            "energy", "utilities", "materials", "real_estate", "comms",
        ]
    )
    stride_small_sector: int = 32
    lora_rank_small_sector: int = 16

    # v4: Targeted synthetic augmentation for failing sectors only
    # Adds modest synthetic data (100 series) to sectors that underperform in v3.
    # Winning sectors (utilities, industrials, financials, tech, cons_disc)
    # train on real data only — synthetic was hurting them.
    synthetic_count_failing: int = 100
    synthetic_sectors: list = field(
        default_factory=lambda: [
            "comms", "real_estate", "energy", "materials",
            "cons_staples", "healthcare",
        ]
    )

    # Output
    save_dir: str = "./lora_adapters"
