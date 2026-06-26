from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_i_common import guardrails, load_phase_three_i_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_i_inputs()
    prior = inputs["neutrino_basis_scale_resolution_attempt"]
    return {
        "artifact": "BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_I_INTERACTION_THEOREM_CLOSURE",
        "theorem_name": "neutrino Dirac-Majorana basis and scale theorem",
        "theorem_status": "OPEN_EXACT_MISSING_THEOREM",
        "prior_blocker_status": prior["scale_resolution_status"],
        "K_nu_status": "BOUNDARY_OPERATOR_SOURCE_ONLY",
        "candidate_neutrino_basis": "PMNS charged-current target labels only",
        "basis_status": "PARTIAL_FOR_PMNS_TARGET_LABELS",
        "candidate_dirac_majorana_convention": "undefined",
        "dirac_majorana_status": "OPEN",
        "candidate_scale_symbol": "Lambda_nu",
        "candidate_scale_expression": "undefined pending dimensional-scale theorem",
        "scale_status": "OPEN",
        "source_artifacts_checked": source_artifact_list(),
        "derived_from_repo_artifact": False,
        "derived_conditional_from_author_axiom": False,
        "standard_target_convention_used": True,
        "affected_vertex_family": "neutral_operator_kernel_BH",
        "promotes_neutral_kernel": False,
        "promotion_status": "FORBIDDEN_TO_PROMOTE_WITHOUT_NEW_THEOREM",
        "missing_if_open": (
            "basis map U_nu, dimensional scale Lambda_nu, and Dirac/Majorana convention "
            "for turning K_nu into a production collider mass or interaction matrix"
        ),
        "forbidden_promotions": [
            "K_nu_as_physical_neutrino_mass_matrix",
            "neutral_operator_kernel_BH_to_feynrules_ready",
            "neutral_operator_kernel_BH_to_ufo_ready",
        ],
        "mass_width_dependency": "OPEN_UNTIL_NEUTRINO_SCALE_AND_CONVENTION_CLOSE",
        "renormalization_dependency": "OPEN_UNTIL_NEUTRINO_SCALE_AND_CONVENTION_CLOSE",
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "K_nu remains a BHSM boundary/operator source. PMNS charged-current target labels "
            "are usable in collider-interface mode, but they do not promote neutral_operator_kernel_BH."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-I neutrino Dirac-Majorana theorem attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

