from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_j_common import guardrails, load_phase_three_j_inputs, minimal_subset_notice, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_minimal_bounded_lagrangian_subset_v1_2.json"


def included_term(
    term_id: str,
    expression: str,
    basis_status: str,
    field_status: str,
    lorentz_status: str,
    gauge_status: str,
    coupling_status: str,
    notes: str,
) -> dict[str, object]:
    return {
        "term_id": term_id,
        "symbolic_expression": expression,
        "included_in_minimal_subset": True,
        "exclusion_reason_if_excluded": "",
        "source_artifacts": source_artifact_list(),
        "basis_status": basis_status,
        "field_dictionary_status": field_status,
        "lorentz_structure_status": lorentz_status,
        "gauge_structure_status": gauge_status,
        "coupling_status": coupling_status,
        "mass_width_status": "RUNTIME_OR_NOT_APPLICABLE",
        "renormalization_status": "OPEN_FOR_PRODUCTION",
        "runtime_parameter_mode": "BHSM_COLLIDER_INTERFACE",
        "is_complete_4d_term": False,
        "is_feynrules_translation_candidate": True,
        "is_production_feynrules_ready": False,
        "is_ufo_ready": False,
        "missing_for_translation": [
            "complete particle table",
            "parameter-card syntax",
            "FeynRules syntax export",
            "mass-width runtime values",
            "renormalization scheme",
        ],
        "notes": notes,
    }


def excluded_term(term_id: str, expression: str, reason: str) -> dict[str, object]:
    return {
        "term_id": term_id,
        "symbolic_expression": expression,
        "included_in_minimal_subset": False,
        "exclusion_reason_if_excluded": reason,
        "source_artifacts": source_artifact_list(),
        "basis_status": "NOT_INCLUDED_IN_MINIMAL_SUBSET",
        "field_dictionary_status": "OPEN_OR_NOT_APPLICABLE",
        "lorentz_structure_status": "OPEN_OR_NOT_APPLICABLE",
        "gauge_structure_status": "OPEN_OR_NOT_APPLICABLE",
        "coupling_status": "OPEN_OR_NOT_APPLICABLE",
        "mass_width_status": "OPEN_OR_NOT_APPLICABLE",
        "renormalization_status": "OPEN_OR_NOT_APPLICABLE",
        "runtime_parameter_mode": "NOT_ALLOWED_IN_MINIMAL_SUBSET",
        "is_complete_4d_term": False,
        "is_feynrules_translation_candidate": False,
        "is_production_feynrules_ready": False,
        "is_ufo_ready": False,
        "missing_for_translation": [reason],
        "notes": "Excluded by Phase Three-J bounded-scope rules.",
    }


def build_payload() -> dict[str, object]:
    load_phase_three_j_inputs()
    return {
        "artifact": "BHSM_minimal_bounded_lagrangian_subset_v1_2",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_J_MINIMAL_COLLIDER_LAGRANGIAN",
        "model_name": "BHSM_MINIMAL_COLLIDER_INTERFACE_SUBSET",
        "parameter_mode": "BHSM_COLLIDER_INTERFACE",
        "subset_statement": minimal_subset_notice(),
        "included_terms": [
            "L_kin_canonical_basis",
            "L_gauge_target_convention",
            "L_CKM_charged_current_bounded",
            "L_PMNS_charged_current_bounded",
        ],
        "excluded_terms": [
            "L_charged_boundary_response_candidate",
            "L_neutral_operator_candidate",
            "L_CP_holonomy_standalone_candidate",
            "L_BHSM_pure_no_fit_mass_width",
            "L_full_renormalization_closure",
        ],
        "terms": [
            included_term(
                "L_kin_canonical_basis",
                "canonical kinetic terms in the Phase Three-F production basis",
                "CANONICAL_PRODUCTION_BASIS_DEFINED",
                "EXPLICIT_FIELD_DICTIONARY_CANDIDATE",
                "STANDARD_HEP_TARGET_CONVENTION",
                "STANDARD_HEP_TARGET_CONVENTION",
                "NOT_APPLICABLE_TO_KINETIC_TERM",
                "Canonical production-basis kinetic structure is a translation candidate only.",
            ),
            included_term(
                "L_gauge_target_convention",
                "standard target gauge kinetic and gauge-current convention terms",
                "CANONICAL_PRODUCTION_BASIS_DEFINED",
                "GAUGE_FIELD_TARGET_DICTIONARY_CANDIDATE",
                "STANDARD_HEP_TARGET_CONVENTION",
                "STANDARD_HEP_TARGET_CONVENTION",
                "SCHEME_CONDITIONAL",
                "Gauge structure is a target convention; production coupling closure remains scheme-conditional.",
            ),
            included_term(
                "L_CKM_charged_current_bounded",
                "(g2_BH_runtime / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.",
                "CANONICAL_PRODUCTION_BASIS_DEFINED",
                "EXPLICIT_FIELD_DICTIONARY_CANDIDATE",
                "STANDARD_HEP_TARGET_CONVENTION",
                "STANDARD_HEP_TARGET_CONVENTION",
                "BHSM_COLLIDER_INTERFACE_RUNTIME_PARAMETER",
                "Uses the BHSM CKM source matrix with standard charged-current target convention.",
            ),
            included_term(
                "L_PMNS_charged_current_bounded",
                "(g2_BH_runtime / sqrt(2)) * ellbar_i gamma^mu P_L U_PMNS_BH[i,j] nu_j W_minus_mu + h.c.",
                "CANONICAL_PRODUCTION_BASIS_DEFINED",
                "EXPLICIT_FIELD_DICTIONARY_CANDIDATE",
                "STANDARD_HEP_TARGET_CONVENTION",
                "STANDARD_HEP_TARGET_CONVENTION",
                "BHSM_COLLIDER_INTERFACE_RUNTIME_PARAMETER",
                "Uses the BHSM PMNS source matrix with standard charged-current target convention.",
            ),
            excluded_term(
                "L_charged_boundary_response_candidate",
                "C_ch_boundary coupled through X_ch",
                "X_ch theorem missing for separate boundary response",
            ),
            excluded_term(
                "L_neutral_operator_candidate",
                "K_nu neutral operator candidate",
                "neutrino physical basis/scale/Dirac-Majorana theorem missing",
            ),
            excluded_term(
                "L_CP_holonomy_standalone_candidate",
                "exp(i delta_BH) O_int + h.c.",
                "O_int theorem missing",
            ),
            excluded_term(
                "L_BHSM_pure_no_fit_mass_width",
                "pure no-fit mass-width closure",
                "pure no-fit mass-width closure missing",
            ),
            excluded_term(
                "L_full_renormalization_closure",
                "full renormalization closure",
                "renormalization closure missing",
            ),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-J minimal bounded Lagrangian subset.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

