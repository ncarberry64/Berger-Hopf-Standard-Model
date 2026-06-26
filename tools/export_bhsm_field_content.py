from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_field_content_export_v0_2.json"


SECTORS = [
    ("charged_lepton_sector", "lepton", "artifacts/charged_boundary_bridge_values_v1.json"),
    ("up_quark_sector", "up_quark", "artifacts/charged_boundary_bridge_values_v1.json"),
    ("down_quark_sector", "down_quark", "artifacts/charged_boundary_bridge_values_v1.json"),
    ("neutral_sector", "neutral", "artifacts/neutral_operator_no_fit_output_v1.json"),
    ("weak_mixing_sector", "weak_mixing", "artifacts/PMNS_no_fit_operator_output_v1.json"),
    ("ckm_sector", "ckm_mixing", "artifacts/CKM_no_fit_operator_output_v1.json"),
    ("pmns_sector", "pmns_mixing", "artifacts/PMNS_no_fit_operator_output_v1.json"),
    ("cp_holonomy_sector", "cp_holonomy", "artifacts/CP_no_fit_holonomy_output_v1.json"),
]


def build_entries() -> list[dict[str, object]]:
    entries = []
    for entry_id, sector, artifact in SECTORS:
        entries.append(
            {
                "field_entry_id": entry_id,
                "sector": sector,
                "candidate_field_name": None,
                "source_artifact": artifact,
                "source_status": "SYMBOLIC_MAPPING_ONLY",
                "spin": None,
                "mass_parameter": None,
                "width_parameter": None,
                "charge": None,
                "color_representation": None,
                "weak_representation": None,
                "generation": None,
                "pdg_id": None,
                "ufo_ready": False,
                "missing_for_ufo": [
                    "complete collider-ready 4D Lagrangian",
                    "particle field normalization",
                    "spin/charge/color/weak representation convention",
                    "mass and width convention",
                    "PDG ID assignment from pinned source",
                ],
                "notes": "Mapped from existing BHSM internal artifact as a sector-level source only; not a complete particle field row.",
            }
        )
    return entries


def build_payload() -> dict[str, object]:
    return {
        "artifact": "BHSM_field_content_export_v0_2",
        "release_basis": "v1.0.1",
        "field_content_source": "existing BHSM internal artifacts only",
        "field_content_complete_for_ufo": False,
        "entries": build_entries(),
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM phase-two field-content source ledger.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
