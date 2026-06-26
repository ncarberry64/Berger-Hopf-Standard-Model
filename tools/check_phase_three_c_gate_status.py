from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_c_common import guardrails, load_packet, source_packet_ref, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_c_gate_status_v0_5.json"


def build_payload() -> dict[str, object]:
    packet = load_packet()
    remaining = [
        "complete 4D Lagrangian",
        "gauge/Lorentz structures",
        "vector and fermion normalizations",
        "mass-width scheme",
        "renormalization scheme",
        "production FeynRules model",
        "loadable UFO model",
        "MadGraph validation",
        "LHE/HepMC generation",
        "Athena/CMSSW integration",
    ]
    return {
        "artifact": "BHSM_phase_three_c_gate_status_v0_5",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_C_FIELD_DICTIONARY_AND_VERTEX_TARGET_MAP",
        **source_packet_ref(),
        "field_dictionary_target_exported": True,
        "BHSM_internal_parameter_card_candidate_exported": True,
        "boundary_source_vertex_matrices_exported": True,
        "standard_collider_vertex_targets_identified": True,
        "complete_4d_lagrangian_exported": False,
        "feynrules_ready": False,
        "ufo_ready": False,
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        **guardrails(),
        "remaining_blockers": remaining,
        "recommended_status_language": packet.get("recommended_status_language"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-C gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
