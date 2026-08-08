#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.stratified_scale_flavor_convergence_v14_52 import (  # noqa: E402
    branch_decision,
    completion_payload,
    lambda85_family_projection_no_go,
    power_log_berger_stationarity_contract,
    stratified_scale_weight_ledger,
)


def dump(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    out = ROOT / "artifacts"
    payloads = {
        "BHSM_stratified_scale_weight_ledger_v14_52.json": stratified_scale_weight_ledger(),
        "BHSM_power_log_scale_berger_gate_v14_52.json": power_log_berger_stationarity_contract(),
        "BHSM_lambda85_family_projection_no_go_v14_52.json": lambda85_family_projection_no_go(),
        "BHSM_effective_zero_input_branch_decision_v14_52.json": branch_decision(),
        "BHSM_completion_gate_v14_52.json": completion_payload(),
    }
    for name, payload in payloads.items():
        dump(out / name, payload)
        print(out / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
