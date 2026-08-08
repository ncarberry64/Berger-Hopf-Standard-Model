#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.geometry_first_nonlocal_v14_51 import (  # noqa: E402
    berger_scale_stationarity_contract,
    completion_payload,
    curvature_response_lock,
    internal_trace_reconstruction,
    relative_zeta_scale_law,
)


def dump(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    out = ROOT / "artifacts"
    payloads = {
        "BHSM_internal_representation_trace_reconstruction_v14_51.json": internal_trace_reconstruction(),
        "BHSM_parent_relative_zeta_scale_gate_v14_51.json": relative_zeta_scale_law(),
        "BHSM_full_Berger_scale_stationarity_contract_v14_51.json": berger_scale_stationarity_contract(),
        "BHSM_curvature_response_lock_v14_51.json": curvature_response_lock(),
        "BHSM_completion_gate_v14_51.json": completion_payload(),
    }
    for name, payload in payloads.items():
        dump(out / name, payload)
        print(out / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
