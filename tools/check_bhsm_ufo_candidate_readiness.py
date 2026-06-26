from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_or_empty(relative: str) -> dict[str, object]:
    path = ROOT / relative
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_readiness() -> dict[str, object]:
    manifest = load_or_empty("artifacts/BHSM_ufo_candidate_build_manifest_v0_2.json")
    blockers = load_or_empty("artifacts/BHSM_feynrules_export_blockers_v0_2.json").get("blockers", {})
    return {
        "complete_4d_lagrangian_exported": False,
        "feynman_rules_exported": False,
        "ufo_candidate_built": bool(manifest.get("ufo_candidate_built", False)),
        "loadable_ufo_model": bool(manifest.get("loadable_ufo_model", False)),
        "madgraph_ready": False,
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "blockers": [key for key, value in blockers.items() if value is True],
    }


def main() -> int:
    result = build_readiness()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
