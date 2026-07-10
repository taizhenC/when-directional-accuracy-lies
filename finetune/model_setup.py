"""Load TimesFM 2.5 and attach LoRA adapters."""

import torch.nn as nn


def load_timesfm():
    """Load TimesFM 2.5 base model."""
    import timesfm

    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )
    return model


def create_lora_model(internal_model, rank=16, alpha=32, dropout=0.05):
    """Attach LoRA adapters to transformer attention + FF layers ONLY.

    Skips tokenizer and output projection to preserve pretrained
    input/output representations.
    """
    from peft import LoraConfig, get_peft_model

    # Only target stacked_xf.* layers (the 20 transformer blocks)
    target_modules = [
        name
        for name, module in internal_model.named_modules()
        if isinstance(module, nn.Linear) and name.startswith("stacked_xf.")
    ]

    config = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=target_modules,
        bias="none",
        task_type=None,
    )
    peft_model = get_peft_model(internal_model, config)
    return peft_model
