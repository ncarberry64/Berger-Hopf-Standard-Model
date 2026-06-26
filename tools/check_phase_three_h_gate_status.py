from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_h_common import guardrails, load_required, readiness_false, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_h_gate_status_v1_0.json"


def build_payload() -> dict[str, object]:
    x_ch = load_required("artifacts/BHSM_x_ch_interaction_operator_resolution_attempt_v1_0.json")
    nu = load_required("artifacts/BHSM_neutrino_basis_scale_resolution_attempt_v1_0.json")
    cp = load_required("artifacts/BHSM_cp_holonomy_attachment_resolution_attempt_v1_0.json")
    audit = load_required("artifacts/BHSM_bounded_vertex_promotion_audit_v1_0.json")
    return {
        "artifact": "BHSM_phase_three_h_gate_status_v1_0",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_H_BOUNDED_BLOCKER_RESOLUTION",
        "x_ch_resolution_attempt_exported": x_ch["artifact"] == "BHSM_x_ch_interaction_operator_resolution_attempt_v1_0",
        "neutrino_basis_scale_resolution_attempt_exported": nu["artifact"] == "BHSM_neutrino_basis_scale_resolution_attempt_v1_0",
        "cp_holonomy_attachment_resolution_attempt_exported": cp["artifact"] == "BHSM_cp_holonomy_attachment_resolution_attempt_v1_0",
        "bounded_vertex_promotion_audit_exported": audit["bounded_vertex_promotion_audit_exported"],
        "x_ch_status": "PARTIALLY_RESOLVED_FOR_STANDARD_CHARGED_CURRENT_TARGETS_OR_OPEN_FOR_BOUNDARY_RESPONSE",
        "neutrino_basis_status": "PARTIALLY_RESOLVED_FOR_PMNS_TARGET_OR_OPEN_FOR_NEUTRAL_KERNEL",
        "neutrino_scale_status": "OPEN",
        "cp_holonomy_attachment_status": "PARTIALLY_RESOLVED_FOR_CKM_PMNS_MIXING_VERTICES_OR_OPEN_FOR_STANDALONE_CP_VERTEX",
        "ckm_vertex_bounded_promotion": True,
        "pmns_vertex_bounded_promotion": True,
        "charged_boundary_response_promoted": False,
        "neutral_kernel_promoted": False,
        "standalone_cp_holonomy_vertex_promoted": False,
        "production_vertex_table_complete": False,
        "mass_width_scheme_complete_for_pure_no_fit": False,
        "runtime_mass_width_policy_defined": True,
        "renormalization_scheme_complete": False,
        **readiness_false(),
        **guardrails(),
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "remaining_blockers": [
            "X_ch interaction theorem for charged boundary response",
            "neutrino physical basis/scale/Dirac-Majorana theorem",
            "standalone CP holonomy interaction attachment O_int",
            "complete 4D Lagrangian",
            "production vertex table",
            "mass-width closure for BHSM_PURE_NOFIT",
            "renormalization closure",
            "FeynRules/UFO/MadGraph/LHE/HepMC/Athena/CMSSW readiness",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-H performs bounded blocker resolution attempts for "
            "X_ch, neutrino basis/scale, and CP holonomy attachment. CKM/PMNS "
            "charged-current targets may be partially promoted as bounded "
            "collider-interface targets where standard current conventions, "
            "canonical production basis, and BHSM mixing/holonomy sources already "
            "align. The separate charged boundary response, neutral kernel, and "
            "standalone CP holonomy vertices remain blocked by explicit missing "
            "interaction/basis/scale theorems. This is not production FeynRules/UFO readiness."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-H gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

