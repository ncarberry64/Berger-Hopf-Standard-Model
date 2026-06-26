from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_ufo_export_manifest_v0_1.json"


def _exists(relative: str) -> bool:
    return (ROOT / relative).exists()


def build_manifest() -> dict[str, object]:
    blockers = []
    if not _exists("data/bhsm_lagrangian_template_v0_1.json"):
        blockers.append("lagrangian schema input missing")
    blockers.extend(
        [
            "complete collider-ready 4D physical Lagrangian missing",
            "Feynman rules missing",
            "production UFO model directory missing",
            "real non-template field-content table missing",
            "real non-template parameter card missing",
            "real non-template vertex table missing",
        ]
    )
    return {
        "artifact": "BHSM_ufo_export_manifest_v0_1",
        "release_basis": "v1.0.1",
        "ufo_export_ready": False,
        "complete_4d_lagrangian_exported": False,
        "feynman_rules_exported": False,
        "field_content_validated": _exists("data/bhsm_field_content_template_v0_1.json"),
        "parameter_card_validated": _exists("data/bhsm_parameter_card_template_v0_1.json"),
        "vertex_table_validated": _exists("data/bhsm_vertex_template_v0_1.json"),
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM UFO phase-one manifest.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
