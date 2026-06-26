from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_h_common import guardrails, load_phase_three_h_inputs, vertex_entries, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_bounded_vertex_promotion_audit_v1_0.json"


def row(vertex_family: str, previous: str, post: str, result: str, reason: str, blockers: list[str]) -> dict[str, object]:
    return {
        "vertex_family": vertex_family,
        "previous_status": previous,
        "post_phase_three_h_status": post,
        "promotion_result": result,
        "promotion_reason": reason,
        "remaining_blockers": blockers,
        "pure_no_fit_ready": False,
        "collider_interface_ready": result.startswith("PARTIALLY_PROMOTED"),
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "notes": "Bounded promotion is not production readiness.",
    }


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_h_inputs()
    vertex_entries(inputs)
    return {
        "artifact": "BHSM_bounded_vertex_promotion_audit_v1_0",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_H_BOUNDED_BLOCKER_RESOLUTION",
        "bounded_vertex_promotion_audit_exported": True,
        "entries": [
            row(
                "q_charged_current_CKM_BH",
                "STRUCTURAL_CANDIDATE_WITH_DERIVED_MIXING_MATRIX",
                "BOUNDED_COLLIDER_INTERFACE_TARGET",
                "PARTIALLY_PROMOTED_TO_BOUNDED_COLLIDER_INTERFACE_TARGET",
                "canonical basis, standard charged current, BHSM CKM source, and CP holonomy-in-mixing are identified",
                ["coupling scheme", "mass-width", "renormalization", "parameter-card", "syntax-export"],
            ),
            row(
                "lepton_charged_current_PMNS_BH",
                "STRUCTURAL_CANDIDATE_WITH_DERIVED_MIXING_MATRIX",
                "BOUNDED_COLLIDER_INTERFACE_TARGET",
                "PARTIALLY_PROMOTED_TO_BOUNDED_COLLIDER_INTERFACE_TARGET",
                "canonical basis, standard charged current, BHSM PMNS source, candidate neutrino runtime basis, and CP holonomy-in-mixing are identified",
                ["neutrino mass/scale", "coupling scheme", "mass-width", "renormalization", "parameter-card", "syntax-export"],
            ),
            row(
                "charged_boundary_response_matrix",
                "BLOCKED_BY_MISSING_X_CH_OPERATOR",
                "OPEN_EXACT_MISSING_THEOREM",
                "NOT_PROMOTED",
                "X_ch interaction operator remains missing for the separate boundary-response vertex",
                ["X_ch interaction operator", "Lorentz structure", "gauge representation"],
            ),
            row(
                "neutral_operator_kernel_BH",
                "BLOCKED_BY_NEUTRINO_BASIS_SCALE_CONVENTION",
                "OPEN_EXACT_MISSING_THEOREM",
                "NOT_PROMOTED",
                "physical neutrino basis, scale, and Dirac/Majorana convention remain missing",
                ["neutrino physical basis", "scale", "Dirac/Majorana convention"],
            ),
            row(
                "cp_holonomy_phase_attachment",
                "BLOCKED_BY_MISSING_INTERACTION_ATTACHMENT",
                "PARTIALLY_RESOLVED_FOR_CKM_PMNS_ONLY",
                "NOT_PROMOTED_AS_STANDALONE_VERTEX",
                "delta_BH is attached through CKM/PMNS mixing sources, but standalone O_int is missing",
                ["O_int interaction operator", "gauge/Lorentz structure"],
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-H bounded vertex promotion audit.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

