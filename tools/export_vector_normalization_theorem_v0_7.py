from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_e_common import guardrails, load_phase_three_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_vector_normalization_theorem_v0_7.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_inputs()
    canonical = inputs["canonical_field_target_conventions"]
    vector_entry = next(
        entry for entry in canonical["entries"] if entry["convention_id"] == "vector_gauge_field"
    )
    missing_for_bhsm = [
        "BHSM vector field-strength normalization theorem",
        "derivation of vector kinetic residue from the internal boundary action",
        "gauge fixing compatible with the BHSM boundary-to-4D projection",
        "renormalization convention for production vector fields",
    ]
    return {
        "artifact": "BHSM_vector_normalization_theorem_v0_7",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_E_NORMALIZATION_GAUGE_SCHEME",
        "theorem_name": "BHSM_VECTOR_NORMALIZATION_THEOREM",
        "field_family": "vector_gauge_fields",
        "canonical_target": vector_entry["canonical_kinetic_target"],
        "candidate_Z_A_symbol": "Z_A_target",
        "candidate_Z_A_value": 1,
        "Z_A_status": "STANDARD_HEP_TARGET_CONVENTION",
        "is_BHSM_derived": False,
        "is_standard_target_convention": True,
        "feynrules_ready": False,
        "ufo_ready": False,
        "source_artifacts": source_artifact_list(),
        "missing_for_BHSM_derivation": missing_for_bhsm,
        "missing_for_feynrules": missing_for_bhsm
        + ["complete vertex table", "production parameter-card convention"],
        "missing_for_ufo": missing_for_bhsm
        + ["FeynRules export", "loadable UFO validation", "MadGraph validation"],
        "notes": (
            "Z_A,target = 1 is a canonical interface convention, not a "
            "BHSM-derived vector field-strength prediction."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-E vector normalization theorem status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

