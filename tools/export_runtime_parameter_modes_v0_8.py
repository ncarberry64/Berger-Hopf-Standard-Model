from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_f_common import guardrails, load_phase_three_f_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_runtime_parameter_modes_v0_8.json"


def build_payload() -> dict[str, object]:
    load_phase_three_f_inputs()
    return {
        "artifact": "BHSM_runtime_parameter_modes_v0_8",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_F_PRODUCTION_BASIS_RUNTIME_PARAMS",
        "modes": [
            {
                "mode_name": "BHSM_PURE_NOFIT",
                "mode_purpose": "derivation-only internal BHSM package use",
                "allowed_inputs": ["BHSM-derived internal values", "released boundary no-fit artifacts"],
                "forbidden_inputs": ["PDG masses", "empirical widths", "runtime detector cards", "post-hoc fits"],
                "empirical_derivation_inputs_used": False,
                "empirical_runtime_inputs_allowed": False,
                "can_generate_physical_events": False,
                "can_be_used_for_derivation": True,
                "can_be_used_for_detector_comparison": "limited_or_false_until_mass_width_closure_exists",
                "boundary_predictions_modified_by_runtime_inputs": False,
                "notes": "No external runtime masses or widths are imported in pure no-fit mode.",
            },
            {
                "mode_name": "BHSM_COLLIDER_INTERFACE",
                "mode_purpose": "future detector/event comparison runtime interface",
                "allowed_inputs": [
                    "external mass cards",
                    "external width cards",
                    "simulation runtime settings",
                    "detector comparison inputs",
                ],
                "forbidden_inputs": [
                    "deriving BHSM constants",
                    "retuning boundary coefficients",
                    "modifying frozen predictions",
                ],
                "empirical_derivation_inputs_used": False,
                "empirical_runtime_inputs_allowed": True,
                "can_generate_physical_events": "only_when_runtime_parameter_card_and_validation_inputs_are_supplied",
                "can_be_used_for_derivation": False,
                "can_be_used_for_detector_comparison": "true_only_when_runtime_parameter_card_and_validation_inputs_are_supplied",
                "boundary_predictions_modified_by_runtime_inputs": False,
                "notes": "Runtime empirical values are simulation/comparison inputs only.",
            },
        ],
        "policy_statement": (
            "Runtime empirical values may be allowed only as simulation/comparison inputs. "
            "They must never be used to derive or retune BHSM constants, internal boundary "
            "coefficients, or frozen predictions."
        ),
        **guardrails(),
        "source_artifacts": source_artifact_list(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-F runtime parameter modes.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

