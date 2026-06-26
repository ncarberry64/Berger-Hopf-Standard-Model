from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_d_common import guardrails, phase_three_c_inputs, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_chiral_current_attachment_map_v0_6.json"


def build_payload() -> dict[str, object]:
    inputs = phase_three_c_inputs()
    targets = {entry["vertex_family_id"]: entry for entry in inputs["vertices"]["targets"]}
    entries = [
        {
            "current_family_id": "q_charged_current_CKM_BH",
            "target_expression": "(g_2 / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.",
            "lorentz_structure_status": "STANDARD_HEP_TARGET_CONVENTION",
            "gauge_structure_status": "STANDARD_HEP_TARGET_CONVENTION",
            "mixing_matrix_source": targets["q_charged_current_CKM_BH"]["BHSM_source"],
            "mixing_matrix_status": "DERIVED_FROM_REPO_ARTIFACT",
            "coupling_source": "g2_BH_candidate",
            "coupling_status": "SCHEME_CONDITIONAL",
            "field_dictionary_status": "CANDIDATE",
            "canonical_normalization_status": "TARGET_CONVENTION_PARTIAL",
            "mass_width_scheme_status": "OPEN",
            "renormalization_scheme_status": "OPEN",
            "feynrules_ready": False,
            "ufo_ready": False,
            "missing_for_feynrules": ["mass-width scheme", "renormalization scheme", "field normalizations", "production coupling scheme"],
            "missing_for_ufo": ["FeynRules validation", "UFO vertex export", "MadGraph load validation"],
            "notes": "CKM mixing is sourced from BHSM artifacts; charged-current Lorentz structure is a target convention.",
        },
        {
            "current_family_id": "lepton_charged_current_PMNS_BH",
            "target_expression": "(g_2 / sqrt(2)) * ellbar_i gamma^mu P_L U_PMNS_BH[i,j] nu_j W_minus_mu + h.c.",
            "lorentz_structure_status": "STANDARD_HEP_TARGET_CONVENTION",
            "gauge_structure_status": "STANDARD_HEP_TARGET_CONVENTION",
            "mixing_matrix_source": targets["lepton_charged_current_PMNS_BH"]["BHSM_source"],
            "mixing_matrix_status": "DERIVED_FROM_REPO_ARTIFACT",
            "coupling_source": "g2_BH_candidate",
            "coupling_status": "SCHEME_CONDITIONAL",
            "field_dictionary_status": "CANDIDATE",
            "canonical_normalization_status": "TARGET_CONVENTION_PARTIAL",
            "mass_width_scheme_status": "OPEN",
            "renormalization_scheme_status": "OPEN",
            "feynrules_ready": False,
            "ufo_ready": False,
            "missing_for_feynrules": ["neutrino convention", "mass-width scheme", "renormalization scheme", "production coupling scheme"],
            "missing_for_ufo": ["FeynRules validation", "UFO vertex export", "MadGraph load validation"],
            "notes": "PMNS mixing is sourced from BHSM artifacts; charged-current Lorentz structure is a target convention.",
        },
        {
            "current_family_id": "charged_boundary_response_matrix",
            "target_expression": "Psi_bar_ch C_ch_boundary Psi_ch X_ch",
            "lorentz_structure_status": "UNRESOLVED_BOUNDARY_SOURCE",
            "gauge_structure_status": "UNRESOLVED_BOUNDARY_SOURCE",
            "mixing_matrix_source": ["artifacts/BHSM_boundary_source_matrices_v0_5.json"],
            "mixing_matrix_status": "DERIVED_BOUNDARY_SOURCE_MATRIX",
            "coupling_source": "C_ch_boundary",
            "coupling_status": "BOUNDARY_SOURCE_MATRIX_ONLY",
            "field_dictionary_status": "CANDIDATE",
            "canonical_normalization_status": "OPEN",
            "mass_width_scheme_status": "OPEN",
            "renormalization_scheme_status": "OPEN",
            "feynrules_ready": False,
            "ufo_ready": False,
            "missing_for_feynrules": ["interaction operator X_ch", "Lorentz structure", "gauge representation", "canonical field normalizations"],
            "missing_for_ufo": ["FeynRules rule", "UFO coupling object", "UFO vertex object"],
            "notes": "Boundary-source matrix resolved; interaction operator X_ch unresolved.",
        },
        {
            "current_family_id": "neutral_operator_kernel_BH",
            "target_expression": "Psi_bar_nu K_nu Psi_nu",
            "lorentz_structure_status": "UNRESOLVED_BOUNDARY_SOURCE",
            "gauge_structure_status": "UNRESOLVED_BOUNDARY_SOURCE",
            "mixing_matrix_source": ["artifacts/BHSM_boundary_source_matrices_v0_5.json"],
            "mixing_matrix_status": "DERIVED_BOUNDARY_SOURCE_MATRIX",
            "coupling_source": "K_nu_boundary",
            "coupling_status": "BOUNDARY_SOURCE_MATRIX_ONLY",
            "field_dictionary_status": "CANDIDATE",
            "canonical_normalization_status": "OPEN",
            "mass_width_scheme_status": "OPEN",
            "renormalization_scheme_status": "OPEN",
            "feynrules_ready": False,
            "ufo_ready": False,
            "missing_for_feynrules": ["physical neutrino basis", "scale", "Dirac/Majorana convention", "chirality structure"],
            "missing_for_ufo": ["FeynRules rule", "UFO coupling object", "UFO vertex object"],
            "notes": "Neutral source matrix resolved; physical basis and convention unresolved.",
        },
    ]
    return {
        "artifact": "BHSM_chiral_current_attachment_map_v0_6",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_D",
        "CKM_current_target_identified": True,
        "PMNS_current_target_identified": True,
        "charged_boundary_source_preserved": True,
        "neutral_boundary_source_preserved": True,
        "entries": entries,
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-D chiral current attachment map.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
