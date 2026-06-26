from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIELD_CONTENT = ROOT / "data" / "bhsm_field_content_template_v0_1.json"
DEFAULT_PARAMETER_CARD = ROOT / "data" / "bhsm_parameter_card_template_v0_1.json"
DEFAULT_VERTEX_TABLE = ROOT / "data" / "bhsm_vertex_template_v0_1.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_required_rows(payload: dict[str, Any], key: str) -> bool:
    rows = payload.get(key)
    return isinstance(rows, list) and len(rows) > 0 and all(isinstance(row, dict) for row in rows)


def _is_template(payload: dict[str, Any]) -> bool:
    status = payload.get("template_status")
    if isinstance(status, list):
        return "STRUCTURAL_TEMPLATE_ONLY" in status
    return status == "STRUCTURAL_TEMPLATE_ONLY"


def validate_inputs(field_content: Path, parameter_card: Path, vertex_table: Path) -> dict[str, Any]:
    fields = load_json(field_content)
    parameters = load_json(parameter_card)
    vertices = load_json(vertex_table)
    field_structural = _has_required_rows(fields, "fields")
    parameter_structural = _has_required_rows(parameters, "parameters")
    vertex_structural = _has_required_rows(vertices, "vertices")
    template_only = _is_template(fields) or _is_template(parameters) or _is_template(vertices)
    return {
        "field_content_path": str(field_content),
        "parameter_card_path": str(parameter_card),
        "vertex_table_path": str(vertex_table),
        "field_content_validated": field_structural,
        "parameter_card_validated": parameter_structural,
        "vertex_table_validated": vertex_structural,
        "structural_templates_valid": field_structural and parameter_structural and vertex_structural,
        "real_ufo_inputs_present": not template_only,
        "ufo_export_ready": False,
        "event_generation_ready": False,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate BHSM UFO phase-one inputs.")
    parser.add_argument("--field-content", type=Path, default=DEFAULT_FIELD_CONTENT)
    parser.add_argument("--parameter-card", type=Path, default=DEFAULT_PARAMETER_CARD)
    parser.add_argument("--vertex-table", type=Path, default=DEFAULT_VERTEX_TABLE)
    args = parser.parse_args()
    result = validate_inputs(args.field_content, args.parameter_card, args.vertex_table)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
