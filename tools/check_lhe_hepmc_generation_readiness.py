from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def build_readiness(args: argparse.Namespace) -> dict[str, object]:
    checks = {
        "validated_lagrangian_file": args.lagrangian.exists(),
        "validated_field_content_file": args.field_content.exists(),
        "validated_parameter_card": args.parameter_card.exists(),
        "validated_vertex_table": args.vertex_table.exists(),
        "ufo_export_manifest": args.ufo_manifest.exists(),
        "ufo_model_directory": args.ufo_model_dir.exists() and args.ufo_model_dir.is_dir(),
        "madgraph_available": shutil.which("mg5_aMC") is not None or shutil.which("mg5") is not None,
        "pdg_target_table": args.pdg_targets.exists() if args.require_pdg_targets else None,
    }
    blockers = []
    if not checks["validated_lagrangian_file"]:
        blockers.append("validated Lagrangian file missing")
    else:
        blockers.append("complete collider-ready Lagrangian not certified by phase-one scaffold")
    if not checks["ufo_model_directory"]:
        blockers.append("UFO model directory missing")
    blockers.extend(
        [
            "Feynman rules not exported",
            "LHE generation disabled until real UFO and process cards exist",
            "HepMC generation disabled until real showering pipeline exists",
        ]
    )
    return {
        "event_generation_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "checks": checks,
        "blockers": blockers,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM LHE/HepMC generation readiness.")
    parser.add_argument("--lagrangian", type=Path, default=ROOT / "data" / "bhsm_lagrangian_template_v0_1.json")
    parser.add_argument("--field-content", type=Path, default=ROOT / "data" / "bhsm_field_content_template_v0_1.json")
    parser.add_argument("--parameter-card", type=Path, default=ROOT / "data" / "bhsm_parameter_card_template_v0_1.json")
    parser.add_argument("--vertex-table", type=Path, default=ROOT / "data" / "bhsm_vertex_template_v0_1.json")
    parser.add_argument("--ufo-manifest", type=Path, default=ROOT / "artifacts" / "BHSM_ufo_export_manifest_v0_1.json")
    parser.add_argument("--ufo-model-dir", type=Path, default=ROOT / "ufo" / "BHSM_UFO")
    parser.add_argument("--pdg-targets", type=Path, default=ROOT / "data" / "pdg_targets_template_v0_1.json")
    parser.add_argument("--require-pdg-targets", action="store_true")
    args = parser.parse_args()
    result = build_readiness(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
