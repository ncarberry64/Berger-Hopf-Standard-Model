from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LAGRANGIAN = ROOT / "data" / "bhsm_lagrangian_template_v0_1.json"
REQUIRED_FIELDS = [
    "schema_version",
    "model_name",
    "release_basis",
    "lagrangian_status",
    "spacetime_dimension",
    "gauge_groups",
    "fields",
    "parameters",
    "terms",
    "normalization_conventions",
    "gauge_fixing_status",
    "renormalization_status",
    "source_artifacts",
    "empirical_derivation_inputs_used",
    "boundary_predictions_modified_by_comparison",
    "official_predictions_changed",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_lagrangian(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    template_status = payload.get("template_status", [])
    if isinstance(template_status, str):
        template_status = [template_status]
    complete = payload.get("lagrangian_status") == "COMPLETE_4D_COLLIDER_READY"
    complete = complete and "DO_NOT_USE_FOR_EVENT_GENERATION" not in template_status
    return {
        "input_path": str(path),
        "schema_fields_present": not missing,
        "missing_fields": missing,
        "complete_4d_lagrangian_exported": bool(complete),
        "event_generation_ready": bool(complete and not missing),
        "empirical_derivation_inputs_used": bool(
            payload.get("empirical_derivation_inputs_used", True)
        ),
        "boundary_predictions_modified_by_comparison": bool(
            payload.get("boundary_predictions_modified_by_comparison", True)
        ),
        "official_predictions_changed": bool(payload.get("official_predictions_changed", True)),
        "template_status": template_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate BHSM Lagrangian schema inputs.")
    parser.add_argument("--lagrangian", type=Path, default=DEFAULT_LAGRANGIAN)
    args = parser.parse_args()
    result = validate_lagrangian(args.lagrangian)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
