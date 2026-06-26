from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_field_normalization_ledger_v0_3.json"


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build_entries() -> list[dict[str, Any]]:
    field_payload = load("artifacts/BHSM_field_content_export_v0_2.json")
    entries: list[dict[str, Any]] = []
    for field in field_payload.get("entries", []):
        entries.append(
            {
                "field_or_sector_id": field["field_entry_id"],
                "sector": field["sector"],
                "candidate_field_symbol": field["candidate_field_name"],
                "source_artifacts": [field["source_artifact"], "artifacts/BHSM_field_content_export_v0_2.json"],
                "normalization_source": None,
                "normalization_value": None,
                "normalization_status": "BLOCKED_BY_MISSING_FIELD_NORMALIZATION",
                "canonical_kinetic_term_ready": False,
                "mass_term_ready": False,
                "width_term_ready": False,
                "gauge_representation_ready": False,
                "missing_for_canonical_field": [
                    "canonical 4D kinetic normalization",
                    "mass parameter convention",
                    "width parameter convention",
                    "gauge representation table from pinned source",
                    "field symbol and particle/antiparticle convention",
                ],
                "missing_for_ufo": [
                    "UFO particle row",
                    "UFO mass and width parameter",
                    "UFO charge/color/spin convention",
                ],
                "notes": "Phase Two-A field entry remains a sector-level source, not a normalized 4D field.",
            }
        )
    return entries


def build_payload() -> dict[str, Any]:
    entries = build_entries()
    return {
        "artifact": "BHSM_field_normalization_ledger_v0_3",
        "release_basis": "v1.0.1",
        "field_normalization_complete": False,
        "canonical_kinetic_terms_complete": False,
        "entries": entries,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-A field-normalization ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
