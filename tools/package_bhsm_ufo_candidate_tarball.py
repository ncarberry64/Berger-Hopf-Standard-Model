from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARBALL = ROOT / "artifacts" / "BHSM_UFO_CANDIDATE_BLOCKED_NOT_FOR_ANALYSIS_v0_2.tar.gz"
README_TEXT = """This is not a loadable production UFO model.
This tarball exists only to document missing inputs.
Do not use for MadGraph production, detector simulation, or physics analysis.
"""


def build_manifest(tarball: Path) -> dict[str, object]:
    return {
        "artifact": "BHSM_blocked_ufo_candidate_tarball_manifest_v0_2",
        "tarball": str(tarball),
        "production_ufo_tarball": False,
        "not_for_analysis": True,
        "loadable_ufo_model": False,
        "madgraph_ready": False,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Package a blocked BHSM UFO candidate documentation tarball.")
    parser.add_argument("--output", type=Path, default=DEFAULT_TARBALL)
    args = parser.parse_args()
    if "BLOCKED_NOT_FOR_ANALYSIS" not in args.output.name:
        raise SystemExit("Blocked tarball name must include BLOCKED_NOT_FOR_ANALYSIS")
    temp_dir = ROOT / "ufo_candidate_BLOCKED_NOT_FOR_ANALYSIS"
    temp_dir.mkdir(exist_ok=True)
    (temp_dir / "README_NOT_FOR_ANALYSIS.md").write_text(README_TEXT, encoding="utf-8")
    manifest = build_manifest(args.output)
    (temp_dir / "blocked_tarball_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, "w:gz") as archive:
        archive.add(temp_dir / "README_NOT_FOR_ANALYSIS.md", arcname="README_NOT_FOR_ANALYSIS.md")
        archive.add(temp_dir / "blocked_tarball_manifest.json", arcname="blocked_tarball_manifest.json")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
