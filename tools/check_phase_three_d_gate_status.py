from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_d_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_d_gate_status_v0_6.json"


def build_payload() -> dict[str, object]:
    canonical = load_required("artifacts/BHSM_canonical_field_target_conventions_v0_6.json")
    norms = load_required("artifacts/BHSM_vector_fermion_normalization_status_v0_6.json")
    currents = load_required("artifacts/BHSM_chiral_current_attachment_map_v0_6.json")
    open_gates = load_required("artifacts/BHSM_mass_width_renormalization_open_gates_v0_6.json")
    remaining = [entry["gate_id"] for entry in open_gates["entries"]]
    return {
        "artifact": "BHSM_phase_three_d_gate_status_v0_6",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_D_CANONICAL_CURRENT_ATTACHMENT",
        "canonical_field_target_convention_exported": bool(canonical["canonical_field_target_convention_exported"]),
        "BHSM_Z_H_preserved": bool(canonical["BHSM_Z_H_preserved"]),
        "Z_A_status": norms["Z_A_status"],
        "Z_psi_status": norms["Z_psi_status"],
        "chiral_current_attachment_map_exported": True,
        "CKM_current_target_identified": bool(currents["CKM_current_target_identified"]),
        "PMNS_current_target_identified": bool(currents["PMNS_current_target_identified"]),
        "charged_boundary_source_preserved": bool(currents["charged_boundary_source_preserved"]),
        "neutral_boundary_source_preserved": bool(currents["neutral_boundary_source_preserved"]),
        "mass_width_scheme_complete": False,
        "renormalization_scheme_complete": False,
        "complete_4d_lagrangian_exported": False,
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        **guardrails(),
        "remaining_blockers": remaining + [
            "complete 4D Lagrangian",
            "production FeynRules model",
            "loadable UFO model",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-D exports canonical field target conventions and "
            "chiral current attachment maps for CKM/PMNS sectors. These are "
            "interface conventions and target-current maps, not production "
            "FeynRules/UFO readiness. Mass-width and renormalization schemes remain open."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-D gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
