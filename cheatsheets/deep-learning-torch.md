# Deep learning with PyTorch

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from PyTorch 2.12 docs (docs.pytorch.org)._

## Reference snippet

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Use the accelerator API. Do not hard-code "cuda". The code then works on all devices.
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
scaler = torch.amp.GradScaler(device.type)       # Current API: torch.amp with the device_type argument

model.train()
for x, y in DataLoader(train_ds, batch_size=128, shuffle=True,
                       num_workers=8, pin_memory=True, persistent_workers=True):
    x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
    opt.zero_grad(set_to_none=True)
    with torch.autocast(device_type=device.type):           # Use for the forward pass only. Never use for the backward pass.
        loss = F.cross_entropy(model(x), y)
    scaler.scale(loss).backward()
    scaler.step(opt)
    scaler.update()

# Inference and evaluation
model.eval()
with torch.inference_mode():                                 # Use this, not torch.no_grad(), for evaluation only
    preds = model(x_val.to(device))
```

## Typical usage patterns

- A model is a subclass of `nn.Module` that declares its layers in `__init__` and computes its output in `forward`. Compose blocks with `nn.ModuleList` for each custom architecture, for example a ViT, an MLP, or a transformer block.
- A training step is `opt.zero_grad(set_to_none=True)` → forward → `loss.backward()` → `opt.step()`, with `AdamW` and a `LambdaLR` warmup and decay. The public minimal form is in `JasonLo/best-in-slot:slots/python-ai/pytorch/example/pytorch_example/__init__.py`.
- In full training loops, the HuggingFace `accelerate` library controls the device, AMP, and DDP with `accelerator.prepare(model, opt, dl)`, `accelerator.device`, and `accelerator.backward(loss)`. These loops do not configure `GradScaler` or `DistributedDataParallel` by hand.

## Learnings

- **Mixed precision belongs to one device namespace** → **Mixed precision is one API that takes a device type**. Use `torch.amp.autocast(device_type=...)` and `torch.amp.GradScaler(device_type)` instead of `torch.cuda.amp.autocast` / `torch.cuda.amp.GradScaler`. Then the same loop runs on CPU, CUDA, or MPS.
- **"Stop gradients" means `torch.no_grad()`** → **Inference-only code uses `torch.inference_mode()`**. It also skips the autograd records for versions and views, so it is faster and shows that the code only evaluates. Keep `no_grad` only when autograd uses those tensors later.
- **Code hard-codes `cuda` and checks `torch.cuda.is_available()`** → **Code gets one device from the accelerator API**. Resolve one `device` at the start with `torch.accelerator` or the `accelerate` library. Then all `.to(device)` calls run unchanged on CUDA, MPS, CPU, or many GPUs.

## Agent rules

- ALWAYS use `torch.amp.autocast(device_type=...)` and `torch.amp.GradScaler(device_type)` for mixed precision.
- NEVER use the old `torch.cuda.amp.autocast` or `torch.cuda.amp.GradScaler`.
- ALWAYS put only the forward pass and the loss inside `autocast`.
- NEVER run `.backward()` inside the autocast context.
- ALWAYS scale the loss with `GradScaler` in fp16 or bf16 mixed-precision training: `scaler.scale(loss).backward()` → `scaler.step(opt)` → `scaler.update()`.
- ALWAYS use `torch.inference_mode()` for pure evaluation and inference.
- ALWAYS use `torch.no_grad()` instead of `torch.inference_mode()` when the outputs go back into autograd.
- ALWAYS resolve one `device` at the start.
- ALWAYS move the model and the batches to that device with `.to(device)`.
- NEVER hard-code `"cuda"` or assume that a GPU is present.
- ALWAYS move batch tensors with `.to(device, non_blocking=True)` together with a `pin_memory=True` DataLoader.
- ALWAYS call `super().__init__()` first in an `nn.Module.__init__`.
- ALWAYS use `optimizer.zero_grad(set_to_none=True)`.
- ALWAYS call `model.train()` before the training loop.
- ALWAYS call `model.eval()` before evaluation.
- ALWAYS load checkpoints with `torch.load(..., weights_only=True, map_location=device)`.
- NEVER load an untrusted checkpoint with `torch.load` without `weights_only=True`.
- ALWAYS use `F.scaled_dot_product_attention` for attention.
- NEVER write the softmax(QKᵀ/√d) attention computation by hand.
- ALWAYS set `num_workers`, `pin_memory=True`, and `persistent_workers=True` on training DataLoaders.
- ALWAYS use a `DistributedSampler` under DDP.
- ALWAYS skip the optimizer step when the loss is NaN or Inf.
- ALWAYS seed `random`, `numpy`, and `torch` together when you need reproducible results.
- NEVER configure `DistributedDataParallel`, `GradScaler`, and `autocast` by hand when an accelerator layer can control device, AMP, and DDP.
