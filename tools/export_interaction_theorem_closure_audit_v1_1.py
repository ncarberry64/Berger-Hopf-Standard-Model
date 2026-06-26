from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_i_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_interaction_theorem_closure_audit_v1_1.json"


def build_payload() -> dict[str, object]:
    x_ch = load_required("artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json")
    neutrino = load_required("artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json")
    cp = load_required("artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json")
    return {
        "artifact": "BHSM_interaction_theorem_closure_audit_v1_1",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_I_INTERACTION_THEOREM_CLOSURE",
        "entries": [
            {
                "theorem_id": "X_ch_charged_boundary_response",
                "prior_status": x_ch["prior_blocker_status"],
                "post_phase_three_i_status": x_ch["theorem_status"],
                "closure_result": "NOT_CLOSED_EXACT_MISSING_THEOREM_LOCALIZED",
                "what_was_validated": "W_mu target convention resolves CKM/PMNS charged-current target mediator only.",
                "what_was_invalidated_or_forbidden": (
                    "Promoting charged_boundary_response_matrix without an X_ch theorem is forbidden."
                ),
                "affected_vertices": ["charged_boundary_response_matrix"],
                "promoted_vertices": [],
                "still_blocked_vertices": ["charged_boundary_response_matrix"],
                "smallest_missing_next_object": x_ch["missing_if_open"],
                "feynrules_ready": False,
                "ufo_ready": False,
                "notes": x_ch["notes"],
            },
            {
                "theorem_id": "neutrino_dirac_majorana_basis_scale",
                "prior_status": neutrino["prior_blocker_status"],
                "post_phase_three_i_status": neutrino["theorem_status"],
                "closure_result": "NOT_CLOSED_EXACT_MISSING_THEOREM_LOCALIZED",
                "what_was_validated": "PMNS target labels remain valid for charged-current collider-interface mode.",
                "what_was_invalidated_or_forbidden": (
                    "Promoting K_nu to a physical mass matrix without basis, scale, and "
                    "Dirac/Majorana convention is forbidden."
                ),
                "affected_vertices": ["neutral_operator_kernel_BH"],
                "promoted_vertices": [],
                "still_blocked_vertices": ["neutral_operator_kernel_BH"],
                "smallest_missing_next_object": neutrino["missing_if_open"],
                "feynrules_ready": False,
                "ufo_ready": False,
                "notes": neutrino["notes"],
            },
            {
                "theorem_id": "cp_holonomy_O_int_attachment",
                "prior_status": cp["prior_blocker_status"],
                "post_phase_three_i_status": cp["theorem_status"],
                "closure_result": "NOT_CLOSED_EXACT_MISSING_THEOREM_LOCALIZED",
                "what_was_validated": "delta_BH attachment through CKM/PMNS mixing sources remains partial.",
                "what_was_invalidated_or_forbidden": (
                    "Promoting a standalone CP holonomy vertex without O_int is forbidden."
                ),
                "affected_vertices": ["cp_holonomy_phase_attachment"],
                "promoted_vertices": [],
                "still_blocked_vertices": ["cp_holonomy_phase_attachment"],
                "smallest_missing_next_object": cp["missing_if_open"],
                "feynrules_ready": False,
                "ufo_ready": False,
                "notes": cp["notes"],
            },
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-I interaction theorem closure audit.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

