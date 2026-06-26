from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_j_common import guardrails, load_phase_three_j_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_minimal_runtime_parameter_requirements_v1_2.json"


def requirement(
    parameter_id: str,
    required_for: list[str],
    source_type: str,
    is_bhsm_derived: bool,
    is_runtime_input: bool,
    allowed_pure_nofit: bool,
    status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "parameter_id": parameter_id,
        "required_for": required_for,
        "source_type": source_type,
        "is_BHSM_derived": is_bhsm_derived,
        "is_runtime_input": is_runtime_input,
        "allowed_in_BHSM_PURE_NOFIT": allowed_pure_nofit,
        "allowed_in_BHSM_COLLIDER_INTERFACE": True,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_runtime_input": False,
        "status": status,
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    load_phase_three_j_inputs()
    return {
        "artifact": "BHSM_minimal_runtime_parameter_requirements_v1_2",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_J_MINIMAL_COLLIDER_LAGRANGIAN",
        "parameter_mode": "BHSM_COLLIDER_INTERFACE",
        "numerical_values_inserted": False,
        "source_artifacts": source_artifact_list(),
        "requirements": [
            requirement(
                "g2_BH_runtime",
                ["L_gauge", "L_CC_q_BHSM_CKM", "L_CC_l_BHSM_PMNS"],
                "scheme_runtime_input",
                False,
                True,
                False,
                "REQUIRED_RUNTIME_SCHEME_PARAMETER",
                "Runtime/scheme coupling input only; not used to derive or retune BHSM constants.",
            ),
            requirement(
                "W_mass_runtime",
                ["future particle table", "future propagator setup"],
                "runtime_simulation_input",
                False,
                True,
                False,
                "REQUIRED_RUNTIME_SIMULATION_INPUT",
                "No numerical value is inserted in Phase Three-J.",
            ),
            requirement(
                "W_width_runtime",
                ["future particle table", "future propagator setup"],
                "runtime_simulation_input",
                False,
                True,
                False,
                "REQUIRED_RUNTIME_SIMULATION_INPUT",
                "No numerical value is inserted in Phase Three-J.",
            ),
            requirement(
                "fermion_masses_runtime",
                ["future particle table", "future propagator setup"],
                "runtime_simulation_input",
                False,
                True,
                False,
                "REQUIRED_RUNTIME_SIMULATION_INPUT",
                "Runtime masses do not modify BHSM boundary predictions.",
            ),
            requirement(
                "fermion_widths_runtime",
                ["future particle table", "future propagator setup"],
                "runtime_simulation_input",
                False,
                True,
                False,
                "REQUIRED_RUNTIME_SIMULATION_INPUT",
                "Runtime widths do not modify BHSM boundary predictions.",
            ),
            requirement(
                "neutrino_runtime_convention_for_PMNS_labels",
                ["L_CC_l_BHSM_PMNS"],
                "runtime_label_convention",
                False,
                True,
                False,
                "REQUIRED_LABEL_CONVENTION_FOR_PMNS_INTERFACE",
                "This does not close the neutral K_nu basis/scale/Dirac-Majorana theorem.",
            ),
            requirement(
                "renormalization_scale_runtime",
                ["future parameter card", "future coupling evaluation"],
                "runtime_scheme_input",
                False,
                True,
                False,
                "REQUIRED_RUNTIME_SCHEME_PARAMETER",
                "Renormalization closure remains open for production use.",
            ),
            requirement(
                "CKM_BH_source_matrix",
                ["L_CC_q_BHSM_CKM"],
                "BHSM_source_artifact",
                True,
                False,
                True,
                "BHSM_DERIVED_SOURCE_MATRIX",
                "BHSM CKM source matrix from repo artifacts.",
            ),
            requirement(
                "PMNS_BH_source_matrix",
                ["L_CC_l_BHSM_PMNS"],
                "BHSM_source_artifact",
                True,
                False,
                True,
                "BHSM_DERIVED_SOURCE_MATRIX",
                "BHSM PMNS source matrix from repo artifacts.",
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-J minimal runtime parameter requirements.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

