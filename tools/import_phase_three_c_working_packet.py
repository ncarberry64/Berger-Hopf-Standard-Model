from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_c_common import PACKET, guardrails, load_packet, source_packet_ref, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_c_source_summary_v0_5.json"


def build_summary() -> dict[str, object]:
    packet = load_packet()
    return {
        "artifact": "BHSM_phase_three_c_source_summary_v0_5",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_C_FIELD_DICTIONARY_V0_5",
        "packet_artifact_name": packet.get("artifact_name"),
        "packet_artifact_version": packet.get("artifact_version"),
        "packet_created_utc": packet.get("created_utc"),
        "public_status": packet.get("public_status"),
        "source_packet_present": PACKET.exists(),
        **source_packet_ref(),
        "field_dictionary_entries": len(packet.get("candidate_field_dictionary_v0_5", [])),
        "gauge_dictionary_entries": len(packet.get("gauge_field_dictionary_v0_5", [])),
        "candidate_parameter_entries": len(packet.get("candidate_parameter_card_entries", [])),
        "boundary_source_matrices": sorted(packet.get("boundary_source_matrices", {}).keys()),
        "vertex_source_targets": len(packet.get("candidate_vertex_source_targets", [])),
        "recommended_status_language": packet.get("recommended_status_language"),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize the copied BHSM Phase Three-C working packet.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_summary()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
