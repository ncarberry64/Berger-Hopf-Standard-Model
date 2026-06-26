from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_f_common import guardrails, load_phase_three_f_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_canonical_production_basis_theorem_v0_8.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_f_inputs()
    canonical = inputs["canonical_field_target_conventions"]
    scalar = next(entry for entry in canonical["entries"] if entry["convention_id"] == "scalar_field")
    missing = [
        "complete 4D Lagrangian",
        "production vertex table",
        "mass-width scheme",
        "renormalization scheme",
        "gauge fixing convention",
    ]
    return {
        "artifact": "BHSM_canonical_production_basis_theorem_v0_8",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_F_PRODUCTION_BASIS_RUNTIME_PARAMS",
        "theorem_name": "BHSM_CANONICAL_PRODUCTION_BASIS_THEOREM",
        "theorem_status": "CANONICAL_PRODUCTION_BASIS_DEFINED",
        "production_basis_defined": True,
        "canonical_scalar_basis": scalar["canonical_kinetic_target"],
        "canonical_vector_basis": "-1/4 F_munu F^munu",
        "canonical_fermion_basis": "i psibar gamma^mu D_mu psi",
        "Z_H_status": scalar["classification"],
        "Z_A_prod": 1,
        "Z_A_prod_status": "CANONICAL_PRODUCTION_BASIS_DEFINED",
        "Z_psi_prod": 1,
        "Z_psi_prod_status": "CANONICAL_PRODUCTION_BASIS_DEFINED",
        "is_Z_A_prod_BHSM_dynamical_prediction": False,
        "is_Z_psi_prod_BHSM_dynamical_prediction": False,
        **guardrails(),
        "source_artifacts": source_artifact_list(),
        "missing_for_complete_4d_lagrangian": missing,
        "missing_for_feynrules": missing + ["FeynRules syntax export"],
        "missing_for_ufo": missing + ["FeynRules validation", "loadable UFO validation"],
        "notes": (
            "Z_A,prod = 1 and Z_psi,prod = 1 are production-basis definitions "
            "for canonical FeynRules/UFO fields. They are not empirical fits "
            "and not nontrivial BHSM-derived wavefunction-renormalization predictions."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-F canonical production basis theorem.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

