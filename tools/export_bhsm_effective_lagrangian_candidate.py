from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_effective_lagrangian_candidate_v0_3.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def parameter_values() -> dict[str, Any]:
    path = ROOT / "artifacts" / "BHSM_parameter_card_export_v0_2.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {entry["parameter_name"]: entry["value"] for entry in payload.get("entries", [])}


def term(
    term_id: str,
    symbol: str,
    sector: str,
    expression: str,
    sources: list[str],
    coefficients: list[str],
    values: dict[str, Any],
    fields: list[str],
    status: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "term_id": term_id,
        "term_symbol": symbol,
        "sector": sector,
        "candidate_density_expression": expression,
        "source_artifacts": sources,
        "coefficient_symbols": coefficients,
        "coefficient_values": {key: values.get(key) for key in coefficients},
        "field_symbols": fields,
        "derivation_status": status,
        "ufo_export_status": "BLOCKED",
        "missing_for_production_lagrangian": [
            "boundary-to-4D projection theorem",
            "4D Lorentz/gauge invariant density derivation",
            "canonical field normalization",
            "mass/width scheme",
        ],
        "missing_for_feynrules": [
            "gauge-fixed 4D Lagrangian",
            "complete Lorentz structures",
            "complete vertex table",
            "vertex normalization convention",
        ],
        "missing_for_ufo": [
            "production FeynRules model",
            "UFO particles.py/parameters.py/couplings.py/lorentz.py vertices.py",
            "MadGraph load validation",
        ],
        "notes": notes,
    }


def build_terms() -> list[dict[str, Any]]:
    values = parameter_values()
    return [
        term(
            "profile_scale_term",
            "L_profile",
            "profile_scale",
            "candidate: -kappa_H * V_profile(Phi; Z_H, r_internal_profile)",
            ["artifacts/profile_scale_closure_values_v1.json"],
            ["kappa_H", "Z_H", "r_internal_profile"],
            values,
            ["Phi"],
            "STRUCTURAL_CANDIDATE",
            "Profile-scale invariants are exported internally, but no 4D scalar potential density is derived here.",
        ),
        term(
            "charged_boundary_response_term",
            "L_charged_boundary",
            "charged",
            "candidate: sum_f beta_f * B_f[psi_f, Phi] + kappa_f * K_f[psi_f, Phi]",
            ["artifacts/charged_boundary_bridge_values_v1.json"],
            ["beta_lepton", "kappa_lepton", "beta_up", "kappa_up", "beta_down", "kappa_down"],
            values,
            ["psi_l", "psi_u", "psi_d", "Phi"],
            "STRUCTURAL_CANDIDATE",
            "Charged boundary bridge coefficients are sourced, but a 4D Yukawa or boundary-response operator is not production-derived.",
        ),
        term(
            "neutral_operator_term",
            "L_neutral",
            "neutral",
            "candidate: eta_nu * N_nu[nu] + g_nu * G_nu[nu, Phi]",
            ["artifacts/neutral_operator_no_fit_output_v1.json"],
            ["eta_nu", "g_nu", "beta_nu", "kappa_nu"],
            values,
            ["nu", "Phi"],
            "STRUCTURAL_CANDIDATE",
            "Neutral operator values are exported as BHSM internal outputs; no minimal-SM neutrino Lagrangian is claimed.",
        ),
        term(
            "ckm_mixing_term",
            "L_CKM_mix",
            "ckm",
            "candidate: psi_u_bar * V_CKM_BH * psi_d + h.c.",
            ["artifacts/CKM_no_fit_operator_output_v1.json"],
            ["J_CKM_BH"],
            values,
            ["psi_u", "psi_d"],
            "SYMBOLIC_PLACEHOLDER",
            "CKM boundary source is present, but no gauge-fixed charged-current vertex normalization is exported.",
        ),
        term(
            "pmns_mixing_term",
            "L_PMNS_mix",
            "pmns",
            "candidate: ell_bar * U_PMNS_BH * nu + h.c.",
            ["artifacts/PMNS_no_fit_operator_output_v1.json"],
            ["theta12_nu", "theta23_nu", "theta13_nu", "delta_BH", "J_PMNS_BH"],
            values,
            ["ell", "nu"],
            "SYMBOLIC_PLACEHOLDER",
            "PMNS boundary source is present as an effective-extension screen, not a production neutrino interaction model.",
        ),
        term(
            "cp_holonomy_term",
            "L_CP_holonomy",
            "cp",
            "candidate: delta_BH * H_CP[boundary holonomy]",
            ["artifacts/CP_no_fit_holonomy_output_v1.json"],
            ["delta_BH_CP"],
            values,
            ["psi"],
            "SYMBOLIC_PLACEHOLDER",
            "CP holonomy output is source-traced, but not translated into a full 4D CP-violating vertex set.",
        ),
        term(
            "boundary_transport_term",
            "L_transport_identity",
            "transport",
            "candidate: T_boundary_to_boundary * I_boundary",
            ["artifacts/common_scale_boundary_transport_v1.json"],
            ["boundary_transport_identity"],
            values,
            ["I_boundary"],
            "DERIVED_FROM_REPO_ARTIFACT",
            "Boundary identity transport is exported, but it is not itself a collider interaction term.",
        ),
    ]


def build_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_effective_lagrangian_candidate_v0_3",
        "release_basis": "v1.0.1",
        "projection_stage": "PHASE_THREE_A_CANDIDATE_TERM_LEDGER",
        "complete_4d_collider_ready_lagrangian_exported": False,
        "production_feynrules_ready": False,
        "production_ufo_ready": False,
        "terms": build_terms(),
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
        "notes": "Candidate ledger only; not a production 4D Lagrangian and not Feynman rules.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-A effective Lagrangian candidate ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
