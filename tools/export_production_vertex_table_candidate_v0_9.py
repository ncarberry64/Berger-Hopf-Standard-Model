from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phase_three_g_common import coupling_entries, current_entries, guardrails, load_phase_three_g_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_production_vertex_table_candidate_v0_9.json"


def base_entry(
    vertex_id: str,
    expression: str,
    fields: list[str],
    coupling: dict[str, Any],
    lorentz_status: str,
    gauge_status: str,
    coupling_status: str,
    mixing_source: Any,
    mixing_status: str,
    holonomy_source: Any,
    holonomy_status: str,
    missing: list[str],
    notes: str,
) -> dict[str, object]:
    return {
        "vertex_id": vertex_id,
        "vertex_family": vertex_id,
        "candidate_expression": expression,
        "fields": fields,
        "field_dictionary_status": "CANDIDATE",
        "canonical_basis_status": "CANONICAL_PRODUCTION_BASIS_DEFINED",
        "lorentz_structure": expression,
        "lorentz_structure_status": lorentz_status,
        "gauge_structure": "target or unresolved source structure",
        "gauge_structure_status": gauge_status,
        "coupling_source": coupling["production_coupling_status"],
        "coupling_status": coupling_status,
        "raw_BHSM_source": coupling["raw_BHSM_source"],
        "raw_coefficient_or_matrix": coupling["raw_coefficient_or_matrix"],
        "mixing_source": mixing_source,
        "mixing_status": mixing_status,
        "holonomy_source": holonomy_source,
        "holonomy_status": holonomy_status,
        "mass_width_dependency": "mass-width scheme or runtime policy",
        "mass_width_status": coupling["mass_width_status"],
        "renormalization_dependency": "production renormalization scheme",
        "renormalization_status": coupling["renormalization_status"],
        "runtime_parameter_mode_allowed": "BHSM_COLLIDER_INTERFACE_ONLY_UNTIL_PURE_NOFIT_MASS_WIDTH_CLOSURE",
        "pure_no_fit_ready": False,
        "collider_interface_ready": "partial_until_runtime_parameter_card_exists",
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "missing_for_feynrules": missing,
        "missing_for_ufo": missing + ["FeynRules validation", "UFO vertex export", "MadGraph load validation"],
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_g_inputs()
    couplings = coupling_entries(inputs)
    currents = current_entries(inputs)
    q = couplings["q_charged_current_CKM_BH"]
    l = couplings["lepton_charged_current_PMNS_BH"]
    charged = couplings["charged_boundary_response_matrix"]
    neutral = couplings["neutral_operator_kernel_BH"]
    cp = couplings["cp_holonomy_phase_attachment"]
    entries = [
        base_entry(
            "q_charged_current_CKM_BH",
            "L_CC,q = (g2_BH / sqrt(2)) * ubar_i gamma^mu P_L V_CKM_BH[i,j] d_j W_plus_mu + h.c.",
            ["u_i", "d_j", "W_plus_mu"],
            q,
            "STANDARD_HEP_TARGET_CONVENTION",
            "TARGET_CONVENTION_PARTIAL",
            "SCHEME_CONDITIONAL",
            currents["q_charged_current_CKM_BH"]["mixing_matrix_source"],
            "DERIVED_FROM_REPO_ARTIFACT",
            ["CP_no_fit_holonomy_output_v1"],
            "DERIVED_FROM_REPO_ARTIFACT",
            ["coupling scheme", "mass-width scheme", "renormalization scheme", "runtime parameter card"],
            "CKM charged-current target is structurally identified from BHSM-derived mixing sources.",
        ),
        base_entry(
            "lepton_charged_current_PMNS_BH",
            "L_CC,l = (g2_BH / sqrt(2)) * ellbar_i gamma^mu P_L U_PMNS_BH[i,j] nu_j W_minus_mu + h.c.",
            ["ell_i", "nu_j", "W_minus_mu"],
            l,
            "STANDARD_HEP_TARGET_CONVENTION",
            "TARGET_CONVENTION_PARTIAL",
            "SCHEME_CONDITIONAL",
            currents["lepton_charged_current_PMNS_BH"]["mixing_matrix_source"],
            "DERIVED_FROM_REPO_ARTIFACT",
            ["CP_no_fit_holonomy_output_v1"],
            "DERIVED_FROM_REPO_ARTIFACT",
            ["neutrino convention", "coupling scheme", "mass-width scheme", "renormalization scheme"],
            "PMNS charged-current target is structurally identified from BHSM-derived mixing sources.",
        ),
        base_entry(
            "charged_boundary_response_matrix",
            "Psi_bar_ch C_ch_boundary Psi_ch X_ch",
            ["Psi_ch", "C_ch_boundary", "X_ch"],
            charged,
            "BLOCKED_BY_MISSING_X_CH_OPERATOR",
            "BLOCKED_BY_MISSING_X_CH_OPERATOR",
            "BOUNDARY_SOURCE_MATRIX_ONLY",
            None,
            "NOT_APPLICABLE",
            None,
            "NOT_APPLICABLE",
            ["X_ch projected field/operator", "Lorentz structure", "gauge representation"],
            "C_ch_boundary is preserved as a derived boundary-source matrix only; X_ch is missing.",
        ),
        base_entry(
            "neutral_operator_kernel_BH",
            "Psi_bar_nu K_nu Psi_nu",
            ["Psi_nu", "K_nu"],
            neutral,
            "BLOCKED_BY_NEUTRINO_BASIS_SCALE_CONVENTION",
            "BLOCKED_BY_NEUTRINO_BASIS_SCALE_CONVENTION",
            "BOUNDARY_SOURCE_MATRIX_ONLY",
            None,
            "NOT_APPLICABLE",
            None,
            "NOT_APPLICABLE",
            ["neutrino basis", "scale convention", "Dirac/Majorana convention"],
            "K_nu is preserved as a derived boundary-source matrix only; neutrino basis and scale are missing.",
        ),
        base_entry(
            "cp_holonomy_phase_attachment",
            "G_raw * exp(i*delta_BH) * O_int + h.c.",
            ["G_raw", "delta_BH", "O_int"],
            cp,
            "BLOCKED_BY_MISSING_INTERACTION_ATTACHMENT",
            "BLOCKED_BY_MISSING_INTERACTION_ATTACHMENT",
            "PHASE_SOURCE_ONLY",
            None,
            "NOT_APPLICABLE",
            ["CP_no_fit_holonomy_output_v1"],
            "DERIVED_FROM_REPO_ARTIFACT",
            ["interaction attachment", "O_int interaction operator", "gauge/Lorentz structure"],
            "delta_BH = pi/3 is preserved as a phase source only; interaction attachment is missing.",
        ),
    ]
    return {
        "artifact": "BHSM_production_vertex_table_candidate_v0_9",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_G_VERTEX_TABLE_LAGRANGIAN_CANDIDATE",
        "production_vertex_table_candidate_exported": True,
        "production_vertex_table_complete": False,
        "entries": entries,
        **guardrails(),
        "source_artifacts": source_artifact_list(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-G production vertex table candidate.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

