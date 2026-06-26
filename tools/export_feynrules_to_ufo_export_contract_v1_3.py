from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_k_common import disabled_model_path, guardrails, load_phase_three_k_inputs, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_feynrules_to_ufo_export_contract_v1_3.json"


def build_payload() -> dict[str, object]:
    load_phase_three_k_inputs()
    return {
        "artifact": "BHSM_feynrules_to_ufo_export_contract_v1_3",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_K_FEYNRULES_EXPORT_ATTEMPT",
        "contract_name": "BHSM_MINIMAL_COLLIDER_INTERFACE_FEYNRULES_TO_UFO_CONTRACT",
        "input_model_file": disabled_model_path(),
        "expected_output_directory": "models/ufo/BHSM_Minimal_Collider_Interface",
        "requires_mathematica": True,
        "requires_feynrules": True,
        "requires_feynarts_optional": True,
        "export_command_template": (
            "Get[\"FeynRules`\"]; LoadModel[\"models/feynrules/BHSM_Minimal_Collider_Interface.fr\"]; "
            "WriteUFO[L_BHSM_Minimal, Output -> \"models/ufo/BHSM_Minimal_Collider_Interface\"]"
        ),
        "ufo_export_attempted": False,
        "ufo_export_passed": False,
        "ufo_model_path": "models/ufo/BHSM_Minimal_Collider_Interface",
        "ufo_loadability_tested": False,
        "ufo_loadability_passed": False,
        "missing_for_ufo": [
            "enabled validated .fr model file",
            "Mathematica/FeynRules runtime unavailable",
            "FeynRules syntax validation",
            "complete particle and parameter declarations",
        ],
        "notes": "UFO export is a future contract only. No UFO model is generated or validated in Phase Three-K.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-K FeynRules-to-UFO contract.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

