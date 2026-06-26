from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_d_common import guardrails, phase_three_c_inputs, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_canonical_field_target_conventions_v0_6.json"


def build_payload() -> dict[str, object]:
    inputs = phase_three_c_inputs()
    params = {entry["parameter"]: entry for entry in inputs["parameters"]["entries"]}
    z_h_value = None
    if "kappa_H_BH" in params:
        z_h_value = 1
    entries = [
        {
            "convention_id": "scalar_field",
            "canonical_kinetic_target": "+1/2 partial_mu phi partial^mu phi",
            "field_rescaling": "phi = sqrt(Z_phi) phi_raw",
            "candidate_Z_symbol": "Z_H",
            "candidate_Z_value": z_h_value,
            "classification": "BHSM_DERIVED_VALUE",
            "is_BHSM_derived": True,
            "is_standard_target_convention": False,
            "ufo_ready": False,
            "missing_for_ufo": ["explicit 4D scalar representation", "mass-width scheme", "potential convention"],
            "notes": "Z_H = 1 is preserved from the BHSM profile source, but production scalar UFO export remains blocked.",
        },
        {
            "convention_id": "vector_gauge_field",
            "canonical_kinetic_target": "-1/4 F_munu F^munu",
            "field_rescaling": "A_mu = sqrt(Z_A) A_raw_mu",
            "candidate_Z_symbol": "Z_A_target",
            "candidate_Z_value": 1,
            "classification": "STANDARD_HEP_TARGET_CONVENTION",
            "is_BHSM_derived": False,
            "is_standard_target_convention": True,
            "ufo_ready": False,
            "missing_for_ufo": ["BHSM vector normalization theorem", "gauge fixing", "renormalization scheme"],
            "notes": "Setting Z_A,target = 1 is a canonical field convention for FeynRules-style interfaces, not a BHSM empirical fit and not a BHSM dynamical prediction.",
        },
        {
            "convention_id": "fermion_field",
            "canonical_kinetic_target": "i psibar gamma^mu D_mu psi",
            "field_rescaling": "psi = sqrt(Z_psi) psi_raw",
            "candidate_Z_symbol": "Z_psi_target",
            "candidate_Z_value": 1,
            "classification": "STANDARD_HEP_TARGET_CONVENTION",
            "is_BHSM_derived": False,
            "is_standard_target_convention": True,
            "ufo_ready": False,
            "missing_for_ufo": ["BHSM fermion normalization theorem", "chiral representation proof", "mass-width scheme"],
            "notes": "Setting Z_psi,target = 1 is a canonical field convention for FeynRules-style interfaces, not a BHSM empirical fit and not a BHSM dynamical prediction.",
        },
    ]
    return {
        "artifact": "BHSM_canonical_field_target_conventions_v0_6",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_D",
        "canonical_field_target_convention_exported": True,
        "BHSM_Z_H_preserved": z_h_value == 1,
        "entries": entries,
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-D canonical field target conventions.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
