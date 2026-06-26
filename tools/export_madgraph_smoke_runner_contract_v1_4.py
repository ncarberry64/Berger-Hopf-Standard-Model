from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_l_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_madgraph_smoke_runner_contract_v1_4.json"


def build_payload() -> dict[str, object]:
    preflight = load_required("artifacts/BHSM_software_environment_preflight_v1_4.json")
    entries = {entry["component"]: entry for entry in preflight["entries"]}
    return {
        "artifact": "BHSM_madgraph_smoke_runner_contract_v1_4",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_L_FEYNRULES_SYNTAX_RUNNER",
        "contract_name": "BHSM_MINIMAL_COLLIDER_INTERFACE_MADGRAPH_SMOKE_RUNNER_CONTRACT",
        "requires_loadable_ufo": True,
        "requires_madgraph": True,
        "mg5_script_path": "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5",
        "ufo_model_path": "models/ufo/BHSM_Minimal_Collider_Interface",
        "planned_processes": [
            "u d~ > w+",
            "e+ ve > w+",
        ],
        "smoke_test_attempted": False,
        "smoke_test_passed": False,
        "lhe_generated": False,
        "hepmc_generated": False,
        "missing_for_smoke_test": [
            "loadable UFO model",
            "MadGraph runtime" if not entries["madgraph"]["detected"] else "MadGraph run intentionally not attempted",
            "validated particle naming",
            "runtime parameter card",
        ],
        "notes": "Planned processes are subject to actual particle naming in the exported UFO. No fake events are generated.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-L MadGraph smoke runner contract.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

