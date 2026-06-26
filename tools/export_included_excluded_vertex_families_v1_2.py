from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_j_common import guardrails, load_phase_three_j_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_included_excluded_vertex_families_v1_2.json"


def included(vertex_family: str, reason: str, blockers: list[str]) -> dict[str, object]:
    return {
        "vertex_family": vertex_family,
        "included_in_minimal_subset": True,
        "inclusion_or_exclusion_status": "INCLUDED_BOUNDED_COLLIDER_INTERFACE_TARGET",
        "reason": reason,
        "source_artifacts": source_artifact_list(),
        "remaining_blockers": blockers,
        "allowed_parameter_mode": "BHSM_COLLIDER_INTERFACE",
        "feynrules_translation_candidate": True,
        "production_feynrules_ready": False,
        "ufo_ready": False,
        "notes": "Included only in the bounded FeynRules-prep subset; this is not production readiness.",
    }


def excluded(vertex_family: str, status: str, reason: str, blockers: list[str]) -> dict[str, object]:
    return {
        "vertex_family": vertex_family,
        "included_in_minimal_subset": False,
        "inclusion_or_exclusion_status": status,
        "reason": reason,
        "source_artifacts": source_artifact_list(),
        "remaining_blockers": blockers,
        "allowed_parameter_mode": "NOT_ALLOWED_IN_MINIMAL_SUBSET",
        "feynrules_translation_candidate": False,
        "production_feynrules_ready": False,
        "ufo_ready": False,
        "notes": "Excluded until the named interaction theorem closes.",
    }


def build_payload() -> dict[str, object]:
    load_phase_three_j_inputs()
    return {
        "artifact": "BHSM_included_excluded_vertex_families_v1_2",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_J_MINIMAL_COLLIDER_LAGRANGIAN",
        "entries": [
            included(
                "q_charged_current_CKM_BH",
                "BHSM CKM source matrix and standard charged-current target convention are available.",
                ["coupling scheme", "mass-width runtime values", "renormalization", "FeynRules syntax"],
            ),
            included(
                "lepton_charged_current_PMNS_BH",
                "BHSM PMNS source matrix and standard charged-current target convention are available.",
                ["neutrino runtime label convention", "mass-width runtime values", "renormalization", "FeynRules syntax"],
            ),
            excluded(
                "charged_boundary_response_matrix",
                "EXCLUDED_OPEN_X_CH_THEOREM",
                "X_ch theorem missing for separate boundary response.",
                ["X_ch spin/gauge/Lorentz/coupling theorem"],
            ),
            excluded(
                "neutral_operator_kernel_BH",
                "EXCLUDED_OPEN_NEUTRINO_BASIS_SCALE_DIRAC_MAJORANA_THEOREM",
                "Neutrino physical basis, scale, and Dirac/Majorana theorem missing.",
                ["U_nu basis map", "Lambda_nu scale", "Dirac/Majorana convention"],
            ),
            excluded(
                "cp_holonomy_phase_attachment",
                "EXCLUDED_OPEN_O_INT_THEOREM",
                "Standalone CP O_int theorem missing.",
                ["O_int field content", "O_int Lorentz/gauge structure", "O_int coupling placement"],
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-J included/excluded vertex families.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

