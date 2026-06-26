from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phase_three_c_common import guardrails, load_packet, source_packet_ref, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_vertex_source_target_map_v0_5.json"


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "vertex_family_id": entry["vertex_family_id"],
        "candidate_expression": entry.get("candidate_expression"),
        "BHSM_source": entry.get("BHSM_source"),
        "BHSM_supplies": entry.get("BHSM_supplies"),
        "missing": entry.get("missing", []),
        "status": entry.get("status"),
        "feynrules_ready": False,
        "ufo_ready": False,
    }


def build_payload() -> dict[str, Any]:
    packet = load_packet()
    return {
        "artifact": "BHSM_vertex_source_target_map_v0_5",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_C",
        **source_packet_ref(),
        "standard_collider_vertex_targets_identified": True,
        "feynrules_ready": False,
        "ufo_ready": False,
        "targets": [normalize_entry(entry) for entry in packet["candidate_vertex_source_targets"]],
        **guardrails(),
        "notes": "Vertex targets are source maps only; no production Feynman rules are exported.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-C vertex-source target map.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
