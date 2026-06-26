from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_g_common import guardrails, load_phase_three_g_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json"


def term(term_id: str, expression: str, status: str, complete: bool, modes: list[str], missing: list[str], notes: str) -> dict[str, object]:
    return {
        "term_id": term_id,
        "symbolic_expression": expression,
        "source_artifacts": source_artifact_list(),
        "status": status,
        "is_complete_4d_term": complete,
        "is_production_feynrules_ready": False,
        "is_ufo_ready": False,
        "allowed_parameter_modes": modes,
        "missing_items": missing,
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    load_phase_three_g_inputs()
    return {
        "artifact": "BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_G_VERTEX_TABLE_LAGRANGIAN_CANDIDATE",
        "symbolic_4d_lagrangian_assembly_ledger_exported": True,
        "complete_4d_lagrangian_exported": False,
        "ledger_statement": (
            "This is a symbolic 4D Lagrangian assembly candidate, not a complete "
            "production 4D Lagrangian and not a loadable FeynRules model."
        ),
        "terms": [
            term("L_kin_canonical_basis", "canonical kinetic terms in production basis", "CANONICAL_PRODUCTION_BASIS_DEFINED", False, ["BHSM_PURE_NOFIT", "BHSM_COLLIDER_INTERFACE"], ["particle table", "mass-width scheme", "renormalization scheme"], "Canonical basis is defined, but the production particle table and schemes remain open."),
            term("L_gauge_target", "SU(3)c x SU(2)L x U(1)Y target gauge terms", "TARGET_CONVENTION_PARTIAL", False, ["BHSM_COLLIDER_INTERFACE"], ["gauge fixing", "production coupling scheme"], "Gauge target convention is partial."),
            term("L_CKM_charged_current_candidate", "(g2_BH/sqrt(2))*ubar gamma P_L V_CKM_BH d W + h.c.", "STRUCTURAL_CANDIDATE_WITH_DERIVED_MIXING_MATRIX", False, ["BHSM_COLLIDER_INTERFACE"], ["coupling scheme", "mass-width", "renormalization", "runtime parameter card"], "CKM target current is structurally identified but not production-ready."),
            term("L_PMNS_charged_current_candidate", "(g2_BH/sqrt(2))*ellbar gamma P_L U_PMNS_BH nu W + h.c.", "STRUCTURAL_CANDIDATE_WITH_DERIVED_MIXING_MATRIX", False, ["BHSM_COLLIDER_INTERFACE"], ["neutrino convention", "coupling scheme", "mass-width", "renormalization"], "PMNS target current is structurally identified but not production-ready."),
            term("L_charged_boundary_response_candidate", "Psi_bar_ch C_ch_boundary Psi_ch X_ch", "BLOCKED_BY_MISSING_X_CH_OPERATOR", False, ["BHSM_PURE_NOFIT", "BHSM_COLLIDER_INTERFACE"], ["X_ch operator", "Lorentz structure", "gauge representation"], "Charged boundary source remains blocked by X_ch."),
            term("L_neutral_operator_candidate", "Psi_bar_nu K_nu Psi_nu", "BLOCKED_BY_NEUTRINO_BASIS_SCALE_CONVENTION", False, ["BHSM_PURE_NOFIT", "BHSM_COLLIDER_INTERFACE"], ["neutrino basis", "scale convention", "Dirac/Majorana convention"], "Neutral kernel remains blocked by neutrino basis and scale."),
            term("L_CP_holonomy_candidate", "G_raw exp(i delta_BH) O_int + h.c.", "BLOCKED_BY_MISSING_INTERACTION_ATTACHMENT", False, ["BHSM_PURE_NOFIT", "BHSM_COLLIDER_INTERFACE"], ["interaction attachment", "O_int operator"], "CP holonomy phase source remains blocked by missing interaction attachment."),
            term("L_mass_width_runtime_policy", "runtime mass-width policy", "RUNTIME_POLICY_DEFINED_NOT_PURE_NOFIT_CLOSURE", False, ["BHSM_COLLIDER_INTERFACE"], ["pure no-fit mass-width closure"], "Runtime policy is defined, but pure no-fit mass-width closure remains open."),
            term("L_renormalization_placeholder", "renormalization placeholder", "OPEN", False, ["BHSM_COLLIDER_INTERFACE"], ["renormalization scheme", "threshold/running convention"], "Production renormalization remains open."),
        ],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-G symbolic 4D Lagrangian assembly ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

