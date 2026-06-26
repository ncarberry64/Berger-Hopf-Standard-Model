from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_e_common import guardrails, load_required, readiness_false, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_e_gate_status_v0_7.json"


def build_payload() -> dict[str, object]:
    vector = load_required("artifacts/BHSM_vector_normalization_theorem_v0_7.json")
    fermion = load_required("artifacts/BHSM_fermion_normalization_theorem_v0_7.json")
    gauge = load_required("artifacts/BHSM_gauge_fixing_production_coupling_scheme_v0_7.json")
    mass = load_required("artifacts/BHSM_mass_width_scheme_candidate_v0_7.json")
    renorm = load_required("artifacts/BHSM_renormalization_scheme_candidate_v0_7.json")
    remaining = [
        "BHSM vector normalization theorem",
        "BHSM fermion normalization theorem",
        "gauge fixing convention",
        "production coupling scheme",
        "mass-width scheme",
        "renormalization scheme",
        "complete 4D Lagrangian",
        "production FeynRules model",
        "loadable UFO model",
        "MadGraph validation",
        "LHE/HepMC generation",
        "Athena/CMSSW integration",
    ]
    return {
        "artifact": "BHSM_phase_three_e_gate_status_v0_7",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_E_NORMALIZATION_GAUGE_SCHEME",
        "vector_normalization_exported": vector["artifact"] == "BHSM_vector_normalization_theorem_v0_7",
        "fermion_normalization_exported": fermion["artifact"] == "BHSM_fermion_normalization_theorem_v0_7",
        "Z_A_status": "STANDARD_HEP_TARGET_CONVENTION_NOT_BHSM_DERIVED",
        "Z_psi_status": "STANDARD_HEP_TARGET_CONVENTION_NOT_BHSM_DERIVED",
        "gauge_fixing_scheme_exported": gauge["artifact"] == "BHSM_gauge_fixing_production_coupling_scheme_v0_7",
        "production_coupling_scheme_exported": gauge["production_coupling_status"] == "SCHEME_CONDITIONAL",
        "mass_width_scheme_candidate_exported": mass["artifact"] == "BHSM_mass_width_scheme_candidate_v0_7",
        "renormalization_scheme_candidate_exported": renorm["artifact"] == "BHSM_renormalization_scheme_candidate_v0_7",
        **readiness_false(),
        **guardrails(),
        "remaining_blockers": remaining,
        "recommended_status_language": (
            "BHSM Phase Three-E exports vector/fermion canonical normalization "
            "conventions, gauge-fixing/coupling scheme candidates, and mass-width/"
            "renormalization open-gate ledgers. These are interface conventions "
            "and candidate schemes, not production FeynRules/UFO readiness. A "
            "complete 4D Lagrangian and production vertex table remain open."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-E gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

