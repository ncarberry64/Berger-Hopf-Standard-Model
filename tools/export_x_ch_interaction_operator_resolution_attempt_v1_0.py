from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_h_common import guardrails, load_phase_three_h_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_x_ch_interaction_operator_resolution_attempt_v1_0.json"


def build_payload() -> dict[str, object]:
    load_phase_three_h_inputs()
    return {
        "artifact": "BHSM_x_ch_interaction_operator_resolution_attempt_v1_0",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_H_BOUNDED_BLOCKER_RESOLUTION",
        "blocker_id": "X_ch_interaction_operator",
        "blocker_name": "X_ch interaction operator",
        "prior_status": "OPEN",
        "candidate_resolution": "standard W_mu charged-current mediator for CKM/PMNS target currents only",
        "resolution_status": "PARTIALLY_RESOLVED_FOR_SPECIFIC_VERTEX_FAMILY",
        "source_artifacts_checked": source_artifact_list(),
        "derived_from_repo_artifact": False,
        "derived_conditional_from_author_axiom": False,
        "standard_target_convention_used": True,
        "affected_vertex_families": [
            "q_charged_current_CKM_BH",
            "lepton_charged_current_PMNS_BH",
            "charged_boundary_response_matrix",
        ],
        "promoted_vertex_families": [
            "q_charged_current_CKM_BH",
            "lepton_charged_current_PMNS_BH",
        ],
        "still_blocked_vertex_families": ["charged_boundary_response_matrix"],
        "missing_theorem_if_open": (
            "derive the separate charged boundary-response interaction operator X_ch "
            "from the BHSM boundary-to-4D projection"
        ),
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "CKM/PMNS target-current vertices may use the standard charged weak "
            "current mediator as an interface convention. The separate charged "
            "boundary response matrix is not collapsed into W exchange and remains open."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-H X_ch resolution attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

