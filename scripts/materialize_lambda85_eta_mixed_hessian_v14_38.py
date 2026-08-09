#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from bhsm.interface.completion.lambda85_eta_mixed_hessian_completion_gate_v14_38 import materialize

ROOT = Path(__file__).resolve().parents[1]
for path in materialize(ROOT / "artifacts"):
    print(path)
