from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_ufo_candidate_build_manifest_v0_2.json"
BLOCKED_DIR = ROOT / "ufo_candidate_BLOCKED_NOT_FOR_ANALYSIS"


def load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def blockers() -> list[str]:
    blocker_payload = load("artifacts/BHSM_feynrules_export_blockers_v0_2.json")
    return [key for key, value in blocker_payload.get("blockers", {}).items() if value is True]


def build_manifest(create_blocked_dir: bool = False) -> dict[str, object]:
    remaining = blockers()
    if create_blocked_dir:
        BLOCKED_DIR.mkdir(exist_ok=True)
        (BLOCKED_DIR / "README_NOT_FOR_ANALYSIS.md").write_text(
            "This is not a loadable production UFO model.\n"
            "This directory exists only to document missing inputs.\n"
            "Do not use for MadGraph production, detector simulation, or physics analysis.\n",
            encoding="utf-8",
        )
    return {
        "artifact": "BHSM_ufo_candidate_build_manifest_v0_2",
        "release_basis": "v1.0.1",
        "ufo_candidate_built": False,
        "loadable_ufo_model": False,
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        "blocked_candidate_directory_created": bool(create_blocked_dir),
        "blocked_candidate_directory": str(BLOCKED_DIR) if create_blocked_dir else None,
        "blockers": remaining,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a gated BHSM UFO candidate manifest.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--create-blocked-dir", action="store_true")
    args = parser.parse_args()
    manifest = build_manifest(args.create_blocked_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
