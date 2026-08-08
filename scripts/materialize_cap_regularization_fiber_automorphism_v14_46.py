from __future__ import annotations

import argparse
import json
from pathlib import Path

from bhsm.interface.completion.cap_regularization_fiber_automorphism_v14_46 import (
    cap_regularity_audit,
    completion_payload,
    covariant_operator_basis,
    fiber_automorphism_audit,
    modulus_stationarity_contract,
    no_fit_matching_protocol,
    stellar_structure_contract,
)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "BHSM_cap_regularity_boundary_variation_v14_46.json": cap_regularity_audit(),
        "BHSM_fiber_automorphism_modulus_gate_v14_46.json": {
            "fiber_automorphism": fiber_automorphism_audit(),
            "modulus_stationarity": modulus_stationarity_contract(),
        },
        "BHSM_covariant_neutron_star_bridge_v14_46.json": {
            "covariant_operator_basis": covariant_operator_basis(),
            "stellar_structure": stellar_structure_contract(),
            "no_fit_protocol": no_fit_matching_protocol(),
        },
        "BHSM_completion_gate_v14_46.json": completion_payload(),
    }
    for name, payload in artifacts.items():
        path = output / name
        write_json(path, payload)
        print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
