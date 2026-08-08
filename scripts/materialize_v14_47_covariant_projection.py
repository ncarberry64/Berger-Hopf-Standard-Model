from __future__ import annotations
import argparse
import json
from pathlib import Path
from bhsm.interface.completion.covariant_cap_projection_v14_47 import (
    completion_gate,
    covariant_projection_contract,
    neutron_star_preregistration_contract,
)


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts")
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    payloads = {
        "BHSM_covariant_cap_projection_v14_47.json": covariant_projection_contract(),
        "BHSM_neutron_star_matching_preregistration_v14_47.json": neutron_star_preregistration_contract(),
        "BHSM_completion_gate_v14_47.json": completion_gate(),
    }
    for name, payload in payloads.items():
        path = out / name
        write_json(path, payload)
        print(path.as_posix())


if __name__ == "__main__":
    main()
