"""Loss functions for TimesFM fine-tuning."""

import torch
import torch.nn.functional as F


def quantile_loss(pred_quantiles, target,
                  quantiles=(0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)):
    """Pinball loss across quantile predictions.

    TimesFM 2.5 outputs 10 quantile channels matching the quantiles above.

    Args:
        pred_quantiles: (batch, horizon, 10)
        target: (batch, horizon)
    """
    target = target.unsqueeze(-1)  # (batch, horizon, 1)
    n_q = min(len(quantiles), pred_quantiles.shape[-1])
    total = torch.tensor(0.0, device=target.device)
    for i in range(n_q):
        q = quantiles[i]
        error = target - pred_quantiles[:, :, i : i + 1]
        total = total + torch.mean(torch.max(q * error, (q - 1) * error))
    return total / n_q


def mse_loss(pred_mean, target):
    """MSE on log-transformed predictions — the paper's proven approach."""
    return F.mse_loss(pred_mean, target)


def financial_loss(pred_mean, pred_quantiles, target,
                   loss_type="mse", direction_weight=0.05,
                   quantiles=(0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)):
    """Combined loss: primary (MSE or quantile) + optional direction penalty.

    Args:
        pred_mean: (batch, horizon) — point predictions
        pred_quantiles: (batch, horizon, n_quantiles) — quantile predictions
        target: (batch, horizon)
        loss_type: "mse" or "quantile"
        direction_weight: weight for direction penalty (0.0 to disable)

    Returns:
        (total_loss, primary_loss, direction_loss)
    """
    # Primary loss
    if loss_type == "quantile":
        primary = quantile_loss(pred_quantiles, target, quantiles)
    else:
        primary = mse_loss(pred_mean, target)

    # Direction penalty (light hint)
    if direction_weight > 0 and pred_mean.shape[1] > 1:
        pred_dir = pred_mean[:, 1:] - pred_mean[:, :-1]
        true_dir = torch.sign(target[:, 1:] - target[:, :-1])
        true_labels = (true_dir + 1) / 2
        dir_loss = F.binary_cross_entropy_with_logits(pred_dir, true_labels)
    else:
        dir_loss = torch.tensor(0.0, device=pred_mean.device)

    total = primary + direction_weight * dir_loss
    return total, primary, dir_loss
