"""Data preparation: log-transform, per-series normalization, Dataset class."""

import numpy as np
import torch
from torch.utils.data import Dataset


class LogNormalizer:
    """Per-series log-transform + z-score normalization.

    Pipeline: raw prices -> log(prices) -> z-score per series
    Inverse: z-score inverse -> exp() -> raw prices

    IMPORTANT: fit() must only see training data to prevent look-ahead bias.
    """

    def __init__(self):
        self.stats = {}  # series_id -> (mean, std)

    def fit(self, train_series, series_id):
        """Compute stats from TRAINING data only."""
        log_s = np.log(np.clip(train_series, 1e-8, None))
        self.stats[series_id] = (log_s.mean(), max(log_s.std(), 1e-8))

    def transform(self, series, series_id):
        """Apply frozen train stats to any split."""
        mean, std = self.stats[series_id]
        return (np.log(np.clip(series, 1e-8, None)) - mean) / std

    def fit_transform(self, train_series, series_id):
        self.fit(train_series, series_id)
        return self.transform(train_series, series_id)

    def inverse_transform(self, normalized, series_id):
        mean, std = self.stats[series_id]
        return np.exp(normalized * std + mean)

    def save(self, path):
        """Save normalizer stats for inference."""
        np.savez(path, **{str(k): np.array(v) for k, v in self.stats.items()})

    def load(self, path):
        """Load normalizer stats."""
        data = np.load(path)
        self.stats = {k: (float(v[0]), float(v[1])) for k, v in data.items()}


class TimeSeriesDataset(Dataset):
    """Sliding-window dataset. All data mixed from the start."""

    def __init__(self, all_series, context_len=512, horizon=128, stride=64):
        self.samples = []
        window = context_len + horizon
        for series in all_series:
            if len(series) < window:
                continue
            for start in range(0, len(series) - window + 1, stride):
                ctx = series[start : start + context_len]
                tgt = series[start + context_len : start + window]
                self.samples.append((
                    torch.tensor(ctx, dtype=torch.float32),
                    torch.tensor(tgt, dtype=torch.float32),
                ))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        ctx, tgt = self.samples[idx]
        return ctx, tgt


def collate_fn(batch):
    """Collate batch of (context, target) pairs."""
    contexts = torch.stack([b[0] for b in batch])
    targets = torch.stack([b[1] for b in batch])
    return contexts, targets
