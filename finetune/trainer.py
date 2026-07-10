"""Training loop with early stopping and random context masking."""

import random
import numpy as np
import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts
from torch.utils.data import DataLoader

from finetune.data_prep import collate_fn
from finetune.loss import financial_loss


def seed_everything(seed: int = 42):
    """Seed all RNGs that influence training, for reproducible runs.

    Covers Python ``random`` (context masking), NumPy, and torch CPU+CUDA
    (LoRA init, dropout, DataLoader shuffle). Call this BEFORE LoRA is created
    (so the adapter's random A-matrix init is reproducible) and again before the
    training loop (so shuffle/dropout/masking are isolated from RNG consumed by
    model loading). We intentionally do NOT call
    ``torch.use_deterministic_algorithms(True)``: several TimesFM ops lack
    deterministic CUDA kernels and it would raise — seed-level determinism plus
    reported bootstrap CIs is the standard here, and GPU atomics may still cause
    ~1e-3 run-to-run variation.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _revin_normalize(patched_input, padding_mask):
    """Apply per-patch running-stats normalization (RevIN), matching decode().

    This is critical: the pretrained model expects RevIN-normalized inputs.
    Without this, the model's internal representations are miscalibrated.

    Args:
        patched_input: (batch, n_patches, patch_len) — raw patched values
        padding_mask: (batch, n_patches, patch_len) — bool, True=padded

    Returns:
        normed: (batch, n_patches, patch_len) — RevIN-normalized
        mu: (batch, n_patches, 1) — running mean per patch
        sigma: (batch, n_patches, 1) — running std per patch
    """
    batch_size, n_patches, patch_len = patched_input.shape
    device = patched_input.device

    # Compute running stats across patches (matching decode()'s approach)
    running_n = torch.zeros(batch_size, device=device)
    running_mu = torch.zeros(batch_size, device=device)
    running_sigma = torch.zeros(batch_size, device=device)

    patch_mus = []
    patch_sigmas = []

    for i in range(n_patches):
        patch = patched_input[:, i, :]       # (batch, patch_len)
        mask = padding_mask[:, i, :]          # (batch, patch_len)
        valid = (~mask).float()
        count = valid.sum(dim=-1)             # (batch,)

        # Update running mean
        patch_sum = (patch * valid).sum(dim=-1)
        new_n = running_n + count
        safe_n = torch.clamp(new_n, min=1.0)
        new_mu = (running_mu * running_n + patch_sum) / safe_n

        # Update running variance (Welford-like)
        patch_sq_sum = ((patch ** 2) * valid).sum(dim=-1)
        new_var = (
            (running_sigma ** 2 * running_n +
             running_mu ** 2 * running_n +
             patch_sq_sum) / safe_n - new_mu ** 2
        )
        new_sigma = torch.sqrt(torch.clamp(new_var, min=1e-8))

        running_n = new_n
        running_mu = new_mu
        running_sigma = new_sigma

        patch_mus.append(running_mu.clone())
        patch_sigmas.append(running_sigma.clone())

    # Stack: (batch, n_patches)
    mu = torch.stack(patch_mus, dim=1).unsqueeze(-1)      # (batch, n_patches, 1)
    sigma = torch.stack(patch_sigmas, dim=1).unsqueeze(-1)  # (batch, n_patches, 1)

    # Normalize
    normed = (patched_input - mu) / sigma
    # Zero out padded positions
    normed = torch.where(padding_mask, torch.zeros_like(normed), normed)

    return normed, mu, sigma


def _revin_denormalize(output, mu_last, sigma_last):
    """Reverse RevIN normalization on model output.

    Args:
        output: (batch, ...) — model's normalized output
        mu_last: (batch, 1) — last patch's running mean
        sigma_last: (batch, 1) — last patch's running std

    Returns:
        denormalized output
    """
    return output * sigma_last + mu_last


def decode_forward(model, ctx, horizon):
    """Run a forward pass through TimesFM with proper RevIN normalization.

    Mirrors the model's decode() method but without torch.no_grad(),
    so gradients flow for training.

    Args:
        model: the LoRA-wrapped internal model
        ctx: (batch, context_len) — normalized log-price context
        horizon: int — number of steps to predict

    Returns:
        pred_mean: (batch, horizon)
        pred_quantiles: (batch, horizon, n_quantiles)
    """
    device = next(model.parameters()).device
    batch_size = ctx.shape[0]
    ctx_len = ctx.shape[1]

    # Patch the input
    patch_len = 32
    n_patches = ctx_len // patch_len
    trimmed = ctx[:, -(n_patches * patch_len):]
    patched_input = trimmed.reshape(batch_size, n_patches, patch_len)

    # Padding mask (False = valid, True = padded)
    padding_mask = torch.zeros(batch_size, n_patches, patch_len,
                               dtype=torch.bool, device=device)

    # Apply RevIN normalization (matching pretrained expectations)
    normed_input, mu, sigma = _revin_normalize(patched_input, padding_mask)

    # Forward through the LoRA-wrapped backbone
    output_tuple, _ = model(normed_input, padding_mask.float())

    # h2 = point predictions in RevIN-normalized space
    normed_outputs = output_tuple[2]  # (batch, n_patches, 1280)
    output_patch_len = 128
    n_q = normed_outputs.shape[-1] // output_patch_len  # 10

    # Reshape to (batch, n_patches, output_patch_len, n_quantiles)
    pred_all = normed_outputs.reshape(batch_size, n_patches, output_patch_len, n_q)

    # Take last input patch (predicts the future)
    pred_last = pred_all[:, -1, :, :]  # (batch, 128, 10)

    # Reverse RevIN using the last patch's running stats
    mu_last = mu[:, -1, :]    # (batch, 1)
    sigma_last = sigma[:, -1, :]  # (batch, 1)
    pred_denormed = _revin_denormalize(pred_last, mu_last.unsqueeze(1), sigma_last.unsqueeze(1))

    # Point forecast = median channel (index 5)
    pred_mean = pred_denormed[:, :horizon, 5]   # (batch, horizon)
    pred_q = pred_denormed[:, :horizon, :]       # (batch, horizon, 10)

    return pred_mean, pred_q


def fine_tune(model, train_dataset, val_dataset, config):
    """Single clean training loop. No curriculum phases.

    Args:
        model: PeftModel (LoRA-wrapped TimesFM backbone)
        train_dataset: TimeSeriesDataset
        val_dataset: TimeSeriesDataset
        config: TrainingConfig

    Returns:
        (model, history_dict)
    """
    device = next(model.parameters()).device
    # Reseed before the loaders so shuffle / dropout / context-masking are
    # reproducible and isolated from RNG consumed by model loading + LoRA init.
    seed = getattr(config, "seed", 42)
    seed_everything(seed)
    g = torch.Generator()
    g.manual_seed(seed)
    train_loader = DataLoader(
        train_dataset, batch_size=config.batch_size,
        shuffle=True, collate_fn=collate_fn, drop_last=True, generator=g,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=config.batch_size,
        shuffle=False, collate_fn=collate_fn,
    )

    optimizer = AdamW(
        model.parameters(), lr=config.lr,
        betas=(0.9, 0.999), weight_decay=config.weight_decay,
    )
    scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=config.epochs)

    from peft import get_peft_model_state_dict, set_peft_model_state_dict
    best_val_loss = float("inf")
    best_state = None          # best-val LoRA weights (CPU); None if never improved
    best_epoch = 0
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "lr": []}

    for epoch in range(1, config.epochs + 1):
        model.train()
        epoch_losses = []

        for ctx, tgt in train_loader:
            ctx, tgt = ctx.to(device), tgt.to(device)

            # Random context masking: truncate to random length in [128, ctx_len]
            if config.random_context_mask:
                mask_len = random.randint(config.min_context, ctx.shape[1])
                ctx = ctx[:, -mask_len:]

            pred_mean, pred_q = decode_forward(model, ctx, config.horizon)
            loss, _, _ = financial_loss(
                pred_mean, pred_q, tgt,
                loss_type=config.loss_type,
                direction_weight=config.direction_weight,
            )

            loss.backward()
            clip_grad_norm_(model.parameters(), max_norm=config.grad_clip)
            optimizer.step()
            scheduler.step(epoch + len(epoch_losses) / len(train_loader))
            optimizer.zero_grad()
            epoch_losses.append(loss.item())

        avg_train = np.mean(epoch_losses)

        # Validation
        val_loss = _evaluate_val(model, val_loader, config, device)

        history["train_loss"].append(avg_train)
        history["val_loss"].append(val_loss)
        history["lr"].append(optimizer.param_groups[0]["lr"])

        # Early stopping (only after min_epochs)
        min_epochs = getattr(config, "min_epochs", 30)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_epoch = epoch
            patience_counter = 0
            best_state = {k: v.detach().cpu().clone()
                          for k, v in get_peft_model_state_dict(model).items()}
            model.save_pretrained(config.save_dir + f"/{config.asset_class}_best")
        elif epoch >= min_epochs:
            patience_counter += 1
            if patience_counter >= config.patience:
                print(f"  Early stopping at epoch {epoch} "
                      f"(best val={best_val_loss:.6f})")
                break

        if epoch % 5 == 0 or epoch == 1:
            print(f"  Epoch {epoch:3d}/{config.epochs} | "
                  f"train={avg_train:.6f} | val={val_loss:.6f} | "
                  f"lr={optimizer.param_groups[0]['lr']:.2e}")

        # Spot-check directional accuracy every 10 epochs
        if epoch % 10 == 0:
            dir_acc = _quick_direction_check(model, val_loader, device)
            print(f"         ↳ val direction accuracy (h=1): {dir_acc:.4f}")

    # Reload the best-val weights so we return (and therefore score) the model
    # we actually selected. Early stopping monitors validation, so without this
    # we would score the LAST epoch — up to `patience` epochs past the best.
    # Guarded for the degenerate run where validation never improved.
    if best_state is not None:
        set_peft_model_state_dict(model, best_state)
    history["best_epoch"] = best_epoch
    history["n_epochs_run"] = len(history["train_loss"])
    history["best_val_loss"] = best_val_loss
    return model, history


def _evaluate_val(model, val_loader, config, device):
    """Compute average validation loss."""
    model.eval()
    losses = []
    with torch.no_grad():
        for ctx, tgt in val_loader:
            ctx, tgt = ctx.to(device), tgt.to(device)
            pred_mean, pred_q = decode_forward(model, ctx, config.horizon)
            loss, _, _ = financial_loss(
                pred_mean, pred_q, tgt,
                loss_type=config.loss_type,
                direction_weight=0.0,  # no direction penalty on validation
            )
            losses.append(loss.item())
    model.train()
    return np.mean(losses) if losses else float("inf")


def _quick_direction_check(model, val_loader, device):
    """Fast 1-step directional accuracy on val set (no full eval overhead)."""
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for ctx, tgt in val_loader:
            ctx, tgt = ctx.to(device), tgt.to(device)
            pred_mean, _ = decode_forward(model, ctx, tgt.shape[1])
            # Compare predicted vs actual direction for the first step
            pred_dir = pred_mean[:, 0] - ctx[:, -1]
            actual_dir = tgt[:, 0] - ctx[:, -1]
            correct += ((pred_dir > 0) == (actual_dir > 0)).sum().item()
            total += ctx.shape[0]
    model.train()
    return correct / total if total > 0 else 0.0
