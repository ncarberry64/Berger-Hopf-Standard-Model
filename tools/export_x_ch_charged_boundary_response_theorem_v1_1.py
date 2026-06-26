from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_i_common import guardrails, load_phase_three_i_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_x_ch_charged_boundary_response_theorem_v1_1.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_i_inputs()
    prior = inputs["x_ch_resolution_attempt"]
    return {
        "artifact": "BHSM_x_ch_charged_boundary_response_theorem_v1_1",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_I_INTERACTION_THEOREM_CLOSURE",
        "theorem_name": "X_ch charged boundary-response interaction theorem",
        "theorem_status": "OPEN_EXACT_MISSING_THEOREM",
        "prior_blocker_status": prior["resolution_status"],
        "candidate_X_ch_symbol": "X_ch^mu",
        "candidate_X_ch_expression": "undefined pending boundary-response interaction theorem",
        "candidate_X_ch_interpretation": (
            "X_ch is the projected charged boundary-response carrier that would mediate "
            "the separate charged boundary matrix C_ch_boundary in the canonical production "
            "basis. It is not automatically identical to W_mu."
        ),
        "source_artifacts_checked": source_artifact_list(),
        "derived_from_repo_artifact": False,
        "derived_conditional_from_author_axiom": False,
        "standard_target_convention_used": True,
        "is_identified_with_W_mu": False,
        "is_distinct_boundary_response_operator": True,
        "affected_vertex_family": "charged_boundary_response_matrix",
        "promotes_charged_boundary_response": False,
        "promotion_status": "FORBIDDEN_TO_PROMOTE_WITHOUT_NEW_THEOREM",
        "missing_if_open": (
            "theorem assigning X_ch spin, gauge representation, Lorentz index structure, "
            "field content, and coupling normalization for the separate charged boundary response"
        ),
        "forbidden_promotions": [
            "charged_boundary_response_matrix_to_feynrules_ready",
            "charged_boundary_response_matrix_to_ufo_ready",
            "X_ch_equals_W_mu_for_boundary_response_without_theorem",
        ],
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "The standard W_mu target convention remains valid only for CKM/PMNS charged-current "
            "target vertices already bounded in Phase Three-H. It does not close the separate "
            "charged boundary-response theorem."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-I X_ch charged boundary-response theorem attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

