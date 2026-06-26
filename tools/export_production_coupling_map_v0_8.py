from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phase_three_f_common import guardrails, load_phase_three_f_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_production_coupling_map_v0_8.json"


def vertex_sources(inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        entry["vertex_family_id"]: entry
        for entry in inputs["vertex_source_target_map"].get("targets", [])
    }


def current_sources(inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        entry["current_family_id"]: entry
        for entry in inputs["chiral_current_attachment_map"].get("entries", [])
    }


def entry(
    coupling_family_id: str,
    raw_source: Any,
    raw_coefficient: Any,
    canonical_basis_rule: str,
    production_coupling_status: str,
    lorentz: str,
    gauge: str,
    scheme: str,
    mass: str,
    renorm: str,
    missing: list[str],
    notes: str,
) -> dict[str, object]:
    return {
        "coupling_family_id": coupling_family_id,
        "raw_BHSM_source": raw_source,
        "raw_coefficient_or_matrix": raw_coefficient,
        "canonical_basis_rule": canonical_basis_rule,
        "production_coupling_status": production_coupling_status,
        "lorentz_attachment_status": lorentz,
        "gauge_attachment_status": gauge,
        "scheme_status": scheme,
        "mass_width_status": mass,
        "renormalization_status": renorm,
        "feynrules_ready": False,
        "ufo_ready": False,
        "missing_for_production": missing,
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_f_inputs()
    vertices = vertex_sources(inputs)
    currents = current_sources(inputs)
    q = currents["q_charged_current_CKM_BH"]
    l = currents["lepton_charged_current_PMNS_BH"]
    charged = vertices["charged_boundary_response_matrix"]
    neutral = vertices["neutral_operator_kernel_BH"]
    cp = vertices["cp_holonomy_phase_attachment"]
    return {
        "artifact": "BHSM_production_coupling_map_v0_8",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_F_PRODUCTION_BASIS_RUNTIME_PARAMS",
        "universal_canonical_basis_rule": "G_prod = G_raw / product_a sqrt(Z_a)",
        "canonical_production_basis_reduction": "Z_a = 1 for production fields; therefore G_prod = G_raw",
        "rule_applicability_conditions": [
            "raw BHSM coefficient has a valid 4D Lorentz attachment",
            "gauge representation is assigned",
            "coupling scheme is defined",
            "mass-width scheme requirements are satisfied if needed",
            "renormalization scheme requirements are satisfied if needed",
        ],
        "entries": [
            entry(
                "q_charged_current_CKM_BH",
                q["mixing_matrix_source"],
                "V_CKM_BH with g2_BH_candidate",
                "APPLICABLE",
                "SCHEME_CONDITIONAL",
                q["lorentz_structure_status"],
                q["gauge_structure_status"],
                q["coupling_status"],
                q["mass_width_scheme_status"],
                q["renormalization_scheme_status"],
                q["missing_for_feynrules"] + q["missing_for_ufo"],
                "Canonical basis rule applies to the target current, but production schemes remain open.",
            ),
            entry(
                "lepton_charged_current_PMNS_BH",
                l["mixing_matrix_source"],
                "U_PMNS_BH with g2_BH_candidate",
                "APPLICABLE",
                "SCHEME_CONDITIONAL",
                l["lorentz_structure_status"],
                l["gauge_structure_status"],
                l["coupling_status"],
                l["mass_width_scheme_status"],
                l["renormalization_scheme_status"],
                l["missing_for_feynrules"] + l["missing_for_ufo"],
                "Canonical basis rule applies to the target current, but production schemes remain open.",
            ),
            entry(
                "charged_boundary_response_matrix",
                charged["BHSM_source"],
                charged["BHSM_supplies"],
                "FORMALLY_APPLICABLE",
                "BOUNDARY_SOURCE_MATRIX_ONLY",
                "UNRESOLVED_BOUNDARY_SOURCE",
                "UNRESOLVED_BOUNDARY_SOURCE",
                "OPEN",
                "OPEN",
                "OPEN",
                charged["missing"],
                "Raw charged boundary matrix is exported; interaction operator X_ch is missing.",
            ),
            entry(
                "neutral_operator_kernel_BH",
                neutral["BHSM_source"],
                neutral["BHSM_supplies"],
                "FORMALLY_APPLICABLE",
                "BOUNDARY_SOURCE_MATRIX_ONLY",
                "UNRESOLVED_BOUNDARY_SOURCE",
                "UNRESOLVED_BOUNDARY_SOURCE",
                "OPEN",
                "OPEN",
                "OPEN",
                neutral["missing"],
                "Raw neutral kernel is exported; neutrino basis and scale convention are missing.",
            ),
            entry(
                "cp_holonomy_phase_attachment",
                cp["BHSM_source"],
                cp["BHSM_supplies"],
                "FORMALLY_APPLICABLE",
                "DERIVED_PHASE_SOURCE",
                "OPEN",
                "OPEN",
                "OPEN",
                "OPEN",
                "OPEN",
                cp["missing"],
                "CP holonomy phase is exported; interaction attachment is missing.",
            ),
        ],
        **guardrails(),
        "source_artifacts": source_artifact_list(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-F production coupling map.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

