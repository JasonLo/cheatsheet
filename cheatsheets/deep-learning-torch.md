# Deep learning with PyTorch

_Grounded in JasonLo's repos as of 2026-06-05; current practice per PyTorch 2.12 docs (docs.pytorch.org)._

## Reference snippet

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Device-agnostic: prefer the accelerator API over hard-coding "cuda".
device = torch.accelerator.current_accelerator() if torch.accelerator.is_available() else torch.device("cpu")


class Net(nn.Module):
    def __init__(self, in_dim: int, n_classes: int) -> None:
        super().__init__()                       # ALWAYS call super().__init__() first
        self.fc1 = nn.Linear(in_dim, 256)
        self.fc2 = nn.Linear(256, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.relu(self.fc1(x)))


model = Net(784, 10).to(device)
opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
scaler = torch.amp.GradScaler(device.type)       # modern API: torch.amp, device_type arg

model.train()
for x, y in DataLoader(train_ds, batch_size=128, shuffle=True,
                       num_workers=8, pin_memory=True, persistent_workers=True):
    x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
    opt.zero_grad(set_to_none=True)
    with torch.autocast(device_type=device.type):           # forward only, never backward
        loss = F.cross_entropy(model(x), y)
    scaler.scale(loss).backward()
    scaler.step(opt)
    scaler.update()

# Inference / eval
model.eval()
with torch.inference_mode():                                 # not torch.no_grad() for pure eval
    preds = model(x_val.to(device))
```

## Typical usage patterns

- Subclass `nn.Module`, declare layers in `__init__`, do math in `forward`; compose blocks with `nn.ModuleList`. Reach for it for every custom architecture (ViT, MLP, transformer block).
- Training step: `opt.zero_grad(set_to_none=True)` → forward → `loss.backward()` → `opt.step()`, with `AdamW` + `LambdaLR` warmup/decay. Public minimal form in `JasonLo/best-in-slot:slots/python-ai/pytorch/example/pytorch_example/__init__.py`.
- Real training delegates device/AMP/DDP to HuggingFace `accelerate`: `accelerator.prepare(model, opt, dl)`, `accelerator.device`, `accelerator.backward(loss)` — rather than wiring `GradScaler`/`DistributedDataParallel` by hand.

_(Real training loops, ViT model, DDP and data pipeline are sourced from a private repo and described in generalized form; only the public toy example is cited.)_

## Learnings

- **Mixed precision is opt-in to a `cuda`/`cpu` namespace** → **AMP is device-typed and unified.** `torch.cuda.amp.autocast` / `torch.cuda.amp.GradScaler` are deprecated; use `torch.amp.autocast(device_type=...)` and `torch.amp.GradScaler(device_type)` so the same loop runs on CPU, CUDA, or MPS.
- **"Turn off gradients" means `torch.no_grad()`** → **pure inference wants `torch.inference_mode()`.** Same no-grad effect but also skips version-counter/view bookkeeping, so it's faster and the right intent signal for eval/serving (keep `no_grad` only when you later mutate those tensors in autograd).
- **Hard-code `cuda` and gate on `torch.cuda.is_available()`** → **write device-agnostic code via the accelerator abstraction.** Resolve one `device` (`torch.accelerator` or, in practice here, the `accelerate` library) and `.to(device)` everything; the code then runs unchanged on CUDA/MPS/CPU/multi-GPU.

## Agent rules

- ALWAYS use `torch.amp.autocast(device_type=...)` and `torch.amp.GradScaler(device_type)`; NEVER `torch.cuda.amp.autocast` / `torch.cuda.amp.GradScaler` (deprecated).
- ALWAYS wrap only the forward pass and loss in `autocast`; NEVER run `.backward()` inside the autocast context.
- ALWAYS scale the loss with `GradScaler` (`scaler.scale(loss).backward()` → `scaler.step(opt)` → `scaler.update()`) when training in fp16/bf16 mixed precision.
- ALWAYS use `torch.inference_mode()` for pure eval/inference; reserve `torch.no_grad()` for cases where the outputs re-enter autograd.
- ALWAYS resolve a single `device` and `.to(device)` model and batches; NEVER hard-code `"cuda"` or assume a GPU is present.
- ALWAYS move batch tensors with `.to(device, non_blocking=True)` paired with a `pin_memory=True` DataLoader.
- ALWAYS call `super().__init__()` first in an `nn.Module.__init__`.
- ALWAYS use `optimizer.zero_grad(set_to_none=True)`.
- ALWAYS call `model.train()` before the training loop and `model.eval()` before evaluation.
- ALWAYS load checkpoints with `torch.load(..., weights_only=True, map_location=device)`; NEVER `torch.load` untrusted checkpoints without `weights_only=True`.
- ALWAYS use `F.scaled_dot_product_attention` for attention; NEVER hand-roll the softmax(QKᵀ/√d) computation.
- ALWAYS set `num_workers`, `pin_memory=True`, and `persistent_workers=True` on training DataLoaders; use `DistributedSampler` under DDP.
- ALWAYS guard against non-finite loss (skip the optimizer step on NaN/Inf) rather than letting it corrupt the weights.
- ALWAYS seed `random`, `numpy`, and `torch` together when reproducibility matters.
- NEVER hand-wire `DistributedDataParallel` + `GradScaler` + `autocast` when an accelerator layer can own device/AMP/DDP behind one boundary.
