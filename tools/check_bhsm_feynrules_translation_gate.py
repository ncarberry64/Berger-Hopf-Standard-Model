from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_feynrules_translation_gate_v0_3.json"


def load_or_empty(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    lagrangian = load_or_empty("artifacts/BHSM_effective_lagrangian_candidate_v0_3.json")
    fields = load_or_empty("artifacts/BHSM_field_normalization_ledger_v0_3.json")
    vertices = load_or_empty("artifacts/BHSM_vertex_normalization_ledger_v0_3.json")
    mass_width = load_or_empty("artifacts/BHSM_mass_width_scheme_status_v0_3.json")
    renorm = load_or_empty("artifacts/BHSM_renormalization_scheme_status_v0_3.json")
    gates = {
        "complete_4d_lagrangian_exported": bool(lagrangian.get("complete_4d_collider_ready_lagrangian_exported", False)),
        "field_normalization_complete": bool(fields.get("field_normalization_complete", False)),
        "vertex_normalization_complete": bool(vertices.get("vertex_normalization_complete", False)),
        "mass_width_scheme_complete": bool(mass_width.get("mass_width_scheme_complete", False)),
        "renormalization_scheme_complete": bool(renorm.get("renormalization_scheme_complete", False)),
        "gauge_fixing_complete": False,
        "complete_vertex_table_present": bool(vertices.get("complete_vertex_table_present", False)),
        "production_parameter_card_present": False,
    }
    blockers = [key for key, value in gates.items() if value is False]
    return {
        "artifact": "BHSM_feynrules_translation_gate_v0_3",
        "release_basis": "v1.0.1",
        **gates,
        "feynrules_ready": not blockers,
        "ufo_ready": False if blockers else False,
        "blockers": blockers,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-A FeynRules translation gate.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
