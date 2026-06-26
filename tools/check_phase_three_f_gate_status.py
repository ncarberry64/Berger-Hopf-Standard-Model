from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_f_common import guardrails, load_required, readiness_false, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_f_gate_status_v0_8.json"


def build_payload() -> dict[str, object]:
    basis = load_required("artifacts/BHSM_canonical_production_basis_theorem_v0_8.json")
    modes = load_required("artifacts/BHSM_runtime_parameter_modes_v0_8.json")
    coupling = load_required("artifacts/BHSM_production_coupling_map_v0_8.json")
    policy = load_required("artifacts/BHSM_mass_width_runtime_policy_v0_8.json")
    remaining = [
        "complete 4D Lagrangian",
        "production vertex table",
        "mass-width closure for BHSM_PURE_NOFIT",
        "renormalization closure",
        "FeynRules export",
        "loadable UFO model",
        "MadGraph validation",
        "LHE/HepMC generation",
        "Athena/CMSSW integration",
    ]
    return {
        "artifact": "BHSM_phase_three_f_gate_status_v0_8",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_F_PRODUCTION_BASIS_RUNTIME_PARAMS",
        "canonical_production_basis_defined": bool(basis["production_basis_defined"]),
        "Z_A_prod_status": basis["Z_A_prod_status"],
        "Z_psi_prod_status": basis["Z_psi_prod_status"],
        "Z_A_prod_is_BHSM_dynamical_prediction": basis["is_Z_A_prod_BHSM_dynamical_prediction"],
        "Z_psi_prod_is_BHSM_dynamical_prediction": basis["is_Z_psi_prod_BHSM_dynamical_prediction"],
        "runtime_parameter_modes_exported": modes["artifact"] == "BHSM_runtime_parameter_modes_v0_8",
        "production_coupling_map_exported": coupling["artifact"] == "BHSM_production_coupling_map_v0_8",
        "mass_width_runtime_policy_exported": policy["artifact"] == "BHSM_mass_width_runtime_policy_v0_8",
        "interface_normalization_gate_cleared": True,
        "production_vertex_table_complete": False,
        "mass_width_scheme_complete_for_pure_no_fit": False,
        "runtime_mass_width_policy_defined": True,
        "renormalization_scheme_complete": False,
        **readiness_false(),
        **guardrails(),
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "remaining_blockers": remaining,
        "recommended_status_language": (
            "BHSM Phase Three-F defines the canonical production basis for "
            "FeynRules/UFO interfaces and separates no-fit derivation mode from "
            "collider runtime comparison mode. The interface normalization gate "
            "is cleared by defining Z_A,prod = Z_psi,prod = 1 as canonical "
            "production-basis conventions, not BHSM dynamical predictions. "
            "Complete 4D Lagrangian export, mass-width closure, renormalization "
            "closure, and production vertex tables remain open."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-F gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

