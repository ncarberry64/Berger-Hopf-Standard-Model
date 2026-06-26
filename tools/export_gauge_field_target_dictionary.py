from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from phase_three_c_common import guardrails, load_packet, source_packet_ref, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_gauge_field_target_dictionary_v0_5.json"


def normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "field_entry_id": entry["field_entry_id"],
        "symbol": entry.get("symbol"),
        "field_type": entry.get("field_type"),
        "gauge_group": entry.get("gauge_group"),
        "canonical_kinetic_target": entry.get("canonical_kinetic_target"),
        "BHSM_source": entry.get("BHSM_source"),
        "status": entry.get("status", "STANDARD_HEP_TARGET_WITH_BHSM_COUPLING_CANDIDATE"),
        "production_status": entry.get("production_status", "BLOCKED"),
        "missing": entry.get("missing", []),
        "ufo_ready": False,
    }


def build_payload() -> dict[str, Any]:
    packet = load_packet()
    return {
        "artifact": "BHSM_gauge_field_target_dictionary_v0_5",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_C",
        **source_packet_ref(),
        "gauge_field_target_dictionary_exported": True,
        "completed_bhsm_gauge_theorem": False,
        "production_ufo_ready": False,
        "entries": [normalize_entry(entry) for entry in packet["gauge_field_dictionary_v0_5"]],
        **guardrails(),
        "notes": "Gauge entries are target conventions with BHSM coupling candidates, not completed BHSM production gauge fields.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-C gauge field target dictionary.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
