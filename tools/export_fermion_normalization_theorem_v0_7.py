from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_e_common import guardrails, load_phase_three_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_fermion_normalization_theorem_v0_7.json"


FAMILIES = [
    "lepton_left_doublet",
    "charged_lepton_right",
    "quark_left_doublet",
    "up_quark_right",
    "down_quark_right",
    "neutral_sector",
]


def family_entry(family: str, canonical_target: str) -> dict[str, object]:
    missing_for_bhsm = [
        "BHSM fermion field-strength normalization theorem",
        "chiral representation proof in the boundary-to-4D projection",
        "fermion kinetic residue derivation from internal boundary states",
        "mass-width scheme",
    ]
    if family == "neutral_sector":
        missing_for_bhsm.append("Dirac/Majorana convention")
    return {
        "field_family": family,
        "canonical_target": canonical_target,
        "candidate_Z_psi_symbol": "Z_psi_target",
        "candidate_Z_psi_value": 1,
        "Z_psi_status": "STANDARD_HEP_TARGET_CONVENTION",
        "is_BHSM_derived": False,
        "is_standard_target_convention": True,
        "feynrules_ready": False,
        "ufo_ready": False,
        "missing_for_BHSM_derivation": missing_for_bhsm,
        "missing_for_feynrules": missing_for_bhsm
        + ["complete chiral current table", "production parameter-card convention"],
        "missing_for_ufo": missing_for_bhsm
        + ["FeynRules export", "loadable UFO validation", "MadGraph validation"],
        "notes": (
            "Z_psi,target = 1 is a canonical interface convention, not a "
            "BHSM-derived fermion field-strength prediction."
        ),
    }


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_inputs()
    canonical = inputs["canonical_field_target_conventions"]
    fermion_target = next(
        entry["canonical_kinetic_target"]
        for entry in canonical["entries"]
        if entry["convention_id"] == "fermion_field"
    )
    entries = [family_entry(family, fermion_target) for family in FAMILIES]
    return {
        "artifact": "BHSM_fermion_normalization_theorem_v0_7",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_E_NORMALIZATION_GAUGE_SCHEME",
        "theorem_name": "BHSM_FERMION_NORMALIZATION_THEOREM",
        "Z_psi_status": "STANDARD_HEP_TARGET_CONVENTION",
        "source_artifacts": source_artifact_list(),
        "entries": entries,
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-E fermion normalization theorem status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

