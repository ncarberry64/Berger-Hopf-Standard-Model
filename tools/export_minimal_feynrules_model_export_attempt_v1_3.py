from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_k_common import disabled_model_path, guardrails, load_phase_three_k_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_minimal_feynrules_model_export_attempt_v1_3.json"


def build_payload() -> dict[str, object]:
    load_phase_three_k_inputs()
    model_path = disabled_model_path()
    return {
        "artifact": "BHSM_minimal_feynrules_model_export_attempt_v1_3",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_K_FEYNRULES_EXPORT_ATTEMPT",
        "model_name": "BHSM_MINIMAL_COLLIDER_INTERFACE",
        "model_file_path": model_path,
        "model_file_created": (ROOT / model_path).exists(),
        "model_file_enabled": False,
        "is_complete_bhsm_model": False,
        "is_minimal_collider_interface_subset": True,
        "included_terms": [
            "L_kin",
            "L_gauge",
            "L_CC_q_BHSM_CKM",
            "L_CC_l_BHSM_PMNS",
        ],
        "excluded_terms": [
            "charged_boundary_response_matrix",
            "neutral_operator_kernel_BH",
            "standalone cp_holonomy_phase_attachment",
            "BHSM_PURE_NOFIT mass-width closure",
            "full renormalization closure",
        ],
        "runtime_parameters": [
            "g2_BH_runtime",
            "W_mass_runtime",
            "W_width_runtime",
            "fermion_masses_runtime",
            "fermion_widths_runtime",
            "renormalization_scale_runtime",
        ],
        "bhsm_source_matrices": ["V_CKM_BH", "U_PMNS_BH"],
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "production_feynrules_file_exported": False,
        "feynrules_syntax_status": "SYNTAX_CONTRACT_ONLY_DISABLED_DRAFT",
        "known_syntax_limitations": [
            "Mathematica/FeynRules validation not available in this sprint",
            "particle class declarations are not complete",
            "parameter-card syntax is not complete",
            "index conventions are symbolic",
            "mass-width runtime assignments are not complete",
        ],
        "missing_for_validated_feynrules": [
            "Mathematica runtime",
            "FeynRules package",
            "complete particle class declarations",
            "validated parameter declarations",
            "FeynRules syntax validation",
        ],
        "notes": (
            "A disabled bounded FeynRules draft is exported for review. It is not a production "
            "FeynRules file and cannot be used to claim UFO or MadGraph readiness."
        ),
        "source_artifacts": source_artifact_list(),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-K minimal FeynRules export attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

