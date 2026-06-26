from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phase_three_c_common import guardrails, load_packet, source_packet_ref, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_explicit_4d_field_dictionary_v0_5.json"


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "field_entry_id": entry["field_entry_id"],
        "candidate_symbol": entry.get("candidate_symbol"),
        "field_type": entry.get("field_type"),
        "spin": entry.get("spin"),
        "color_representation": entry.get("color_representation"),
        "weak_representation": entry.get("weak_representation"),
        "hypercharge_target": entry.get("hypercharge_target", entry.get("hypercharge")),
        "hypercharge": entry.get("hypercharge"),
        "source_artifacts": entry.get("source_artifacts", []),
        "BHSM_coefficients": entry.get("BHSM_coefficients", []),
        "known_BHSM_values": entry.get("known_BHSM_values", []),
        "status": entry.get("status", entry.get("field_normalization_status", "CONDITIONAL_FIELD_TARGET")),
        "production_status": entry.get("production_status", "NOT_UFO_READY"),
        "missing": entry.get("missing", []),
        "notes": entry.get("notes", entry.get("warning")),
        "warning": entry.get("warning"),
        "ufo_ready": False,
    }


def build_payload() -> dict[str, Any]:
    packet = load_packet()
    return {
        "artifact": "BHSM_explicit_4d_field_dictionary_v0_5",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_C",
        **source_packet_ref(),
        "field_dictionary_target_exported": True,
        "production_ufo_ready": False,
        "entries": [normalize_entry(entry) for entry in packet["candidate_field_dictionary_v0_5"]],
        **guardrails(),
        "notes": "Candidate 4D field dictionary target only; not a production UFO particle table.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-C explicit 4D field dictionary.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
