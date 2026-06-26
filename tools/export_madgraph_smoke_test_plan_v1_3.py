from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_k_common import guardrails, load_phase_three_k_inputs, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_madgraph_smoke_test_plan_v1_3.json"


def build_payload() -> dict[str, object]:
    load_phase_three_k_inputs()
    return {
        "artifact": "BHSM_madgraph_smoke_test_plan_v1_3",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_K_FEYNRULES_EXPORT_ATTEMPT",
        "plan_name": "BHSM_MINIMAL_COLLIDER_INTERFACE_MADGRAPH_SMOKE_TEST_PLAN",
        "requires_loadable_ufo": True,
        "requires_madgraph": True,
        "minimal_processes": [
            "u d~ > w+",
            "e+ ve > w+",
        ],
        "run_card_template_path": "runs/madgraph_smoke/run_card_template.dat",
        "param_card_template_path": "runs/madgraph_smoke/param_card_template.dat",
        "smoke_test_attempted": False,
        "smoke_test_passed": False,
        "lhe_generated": False,
        "hepmc_generated": False,
        "missing_for_smoke_test": [
            "loadable UFO model",
            "MadGraph runtime",
            "validated particle naming",
            "runtime parameter card",
        ],
        "notes": "This is a smoke-test plan only. No LHE or HepMC files are generated or committed.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-K MadGraph smoke-test plan.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

