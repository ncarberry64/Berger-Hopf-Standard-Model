from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_vertex_normalization_ledger_v0_3.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build_entries() -> list[dict[str, Any]]:
    source_payload = load("artifacts/BHSM_vertex_source_ledger_v0_2.json")
    entries: list[dict[str, Any]] = []
    for source in source_payload.get("entries", []):
        entries.append(
            {
                "vertex_family_id": source["vertex_source_id"],
                "candidate_vertex_symbol": source["coupling_symbol"],
                "sector": source["candidate_interaction_family"],
                "source_artifacts": [source["source_artifact"], "artifacts/BHSM_vertex_source_ledger_v0_2.json"],
                "candidate_fields": source["candidate_fields"],
                "coefficient_symbol": source["coupling_symbol"],
                "coefficient_value": source["coupling_value"],
                "lorentz_structure_status": "BLOCKED_BY_MISSING_4D_PROJECTION_THEOREM",
                "gauge_structure_status": "BLOCKED_BY_MISSING_GAUGE_FIXING",
                "normalization_status": "BLOCKED_BY_MISSING_VERTEX_NORMALIZATION",
                "feynrules_ready": False,
                "ufo_ready": False,
                "missing_for_feynrules": [
                    "complete 4D Lorentz structure",
                    "gauge-fixed interaction term",
                    "canonical field normalization",
                    "vertex normalization convention",
                ],
                "missing_for_ufo": [
                    "UFO coupling object",
                    "UFO Lorentz object",
                    "validated vertices.py entry",
                ],
                "notes": "Source ledger entry is not a production Feynman rule or UFO vertex.",
            }
        )
    return entries


def build_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_vertex_normalization_ledger_v0_3",
        "release_basis": "v1.0.1",
        "vertex_normalization_complete": False,
        "complete_vertex_table_present": False,
        "entries": build_entries(),
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-A vertex-normalization ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
