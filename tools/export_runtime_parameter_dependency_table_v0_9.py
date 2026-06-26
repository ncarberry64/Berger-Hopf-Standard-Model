from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_g_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_runtime_parameter_dependency_table_v0_9.json"


def entry(object_id: str, object_type: str, pure_allowed: bool, collider_allowed: bool, pure_missing: list[str], collider_missing: list[str]) -> dict[str, object]:
    return {
        "object_id": object_id,
        "object_type": object_type,
        "depends_on_runtime_mass_width": True,
        "depends_on_runtime_coupling": True,
        "depends_on_runtime_renormalization_scale": True,
        "allowed_in_BHSM_PURE_NOFIT": pure_allowed,
        "allowed_in_BHSM_COLLIDER_INTERFACE": collider_allowed,
        "empirical_derivation_inputs_used": False,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "missing_for_pure_no_fit": pure_missing,
        "missing_for_collider_interface": collider_missing,
        "notes": "Runtime empirical values are comparison inputs only and do not modify BHSM sources.",
    }


def build_payload() -> dict[str, object]:
    vertices = load_required("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")
    lagrangian = load_required("artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json")
    rows = [
        entry(v["vertex_id"], "vertex", False, True, ["no-fit mass-width closure", "renormalization closure"], ["runtime parameter card", "validation inputs"])
        for v in vertices["entries"]
    ]
    rows.extend(
        entry(t["term_id"], "lagrangian_term", t["term_id"] == "L_kin_canonical_basis", True, ["pure no-fit closure if term is physical"], ["runtime parameter card if simulation is requested"])
        for t in lagrangian["terms"]
    )
    return {
        "artifact": "BHSM_runtime_parameter_dependency_table_v0_9",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_G_VERTEX_TABLE_LAGRANGIAN_CANDIDATE",
        "runtime_parameter_dependency_table_exported": True,
        "policy_statement": (
            "BHSM_PURE_NOFIT uses no empirical runtime inputs. BHSM_COLLIDER_INTERFACE "
            "may use runtime empirical values only as simulation/comparison inputs; "
            "they are not derivation inputs and may not modify BHSM constants, "
            "boundary coefficients, mixing matrices, or frozen predictions."
        ),
        "entries": rows,
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-G runtime parameter dependency table.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

