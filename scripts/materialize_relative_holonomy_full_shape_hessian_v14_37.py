#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from bhsm.interface.completion.relative_holonomy_full_shape_hessian_completion_gate_v14_37 import materialize

ROOT = Path(__file__).resolve().parents[1]
for path in materialize(ROOT / "artifacts"):
    print(path)
