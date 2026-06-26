from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_d_common import guardrails, phase_three_c_inputs, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_vector_fermion_normalization_status_v0_6.json"


def entry(
    field_id: str,
    field_type: str,
    canonical_target: str,
    z_symbol: str,
    z_value: int,
    classification: str,
    is_bhsm: bool,
    is_standard: bool,
    missing: list[str],
    notes: str,
) -> dict[str, object]:
    return {
        "field_or_sector_id": field_id,
        "field_type": field_type,
        "canonical_target": canonical_target,
        "candidate_Z_symbol": z_symbol,
        "candidate_Z_value": z_value,
        "normalization_classification": classification,
        "is_BHSM_derived": is_bhsm,
        "is_standard_target_convention": is_standard,
        "ufo_ready": False,
        "missing_for_production": missing,
        "notes": notes,
    }


def build_payload() -> dict[str, object]:
    phase_three_c_inputs()
    vector_missing = ["BHSM vector normalization theorem", "gauge fixing", "renormalization scheme"]
    fermion_missing = ["BHSM fermion normalization theorem", "chiral representation proof", "mass-width scheme"]
    entries = [
        entry(
            "profile_scalar_H",
            "scalar/profile",
            "+1/2 partial_mu phi partial^mu phi",
            "Z_H",
            1,
            "BHSM_DERIVED_VALUE",
            True,
            False,
            ["explicit 4D scalar representation", "mass-width scheme", "potential convention"],
            "Scalar/profile normalization source Z_H = 1 is preserved from BHSM artifacts.",
        ),
        entry("gauge_gluon_target", "vector gauge field", "-1/4 F_munu F^munu", "Z_A_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, vector_missing, "Target convention only; not a BHSM-derived vector normalization."),
        entry("gauge_weak_target", "vector gauge field", "-1/4 F_munu F^munu", "Z_A_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, vector_missing, "Target convention only; not a BHSM-derived vector normalization."),
        entry("gauge_hypercharge_target", "vector gauge field", "-1/4 F_munu F^munu", "Z_A_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, vector_missing, "Target convention only; not a BHSM-derived vector normalization."),
        entry("lepton_left_doublet", "fermion", "i psibar gamma^mu D_mu psi", "Z_psi_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, fermion_missing, "Target convention only; not a BHSM-derived fermion normalization."),
        entry("charged_lepton_right", "fermion", "i psibar gamma^mu D_mu psi", "Z_psi_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, fermion_missing, "Target convention only; not a BHSM-derived fermion normalization."),
        entry("quark_left_doublet", "fermion", "i psibar gamma^mu D_mu psi", "Z_psi_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, fermion_missing, "Target convention only; not a BHSM-derived fermion normalization."),
        entry("up_quark_right", "fermion", "i psibar gamma^mu D_mu psi", "Z_psi_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, fermion_missing, "Target convention only; not a BHSM-derived fermion normalization."),
        entry("down_quark_right", "fermion", "i psibar gamma^mu D_mu psi", "Z_psi_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, fermion_missing, "Target convention only; not a BHSM-derived fermion normalization."),
        entry("neutral_sector", "fermion/effective neutral", "i psibar gamma^mu D_mu psi", "Z_psi_target", 1, "STANDARD_HEP_TARGET_CONVENTION", False, True, fermion_missing + ["Dirac/Majorana convention"], "Neutral-sector target convention only; physical neutrino basis remains open."),
    ]
    return {
        "artifact": "BHSM_vector_fermion_normalization_status_v0_6",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_D",
        "Z_A_status": "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED",
        "Z_psi_status": "STANDARD_TARGET_CONVENTION_OR_BLOCKED_NOT_BHSM_DERIVED",
        "entries": entries,
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-D vector/fermion normalization status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
