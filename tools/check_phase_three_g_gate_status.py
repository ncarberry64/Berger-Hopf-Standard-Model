from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_g_common import guardrails, load_required, readiness_false, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_g_gate_status_v0_9.json"


def build_payload() -> dict[str, object]:
    vertex = load_required("artifacts/BHSM_production_vertex_table_candidate_v0_9.json")
    lagrangian = load_required("artifacts/BHSM_symbolic_4d_lagrangian_assembly_ledger_v0_9.json")
    readiness = load_required("artifacts/BHSM_vertex_readiness_matrix_v0_9.json")
    blockers = load_required("artifacts/BHSM_feynrules_export_blocker_table_v0_9.json")
    runtime = load_required("artifacts/BHSM_runtime_parameter_dependency_table_v0_9.json")
    return {
        "artifact": "BHSM_phase_three_g_gate_status_v0_9",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_G_VERTEX_TABLE_LAGRANGIAN_CANDIDATE",
        "production_vertex_table_candidate_exported": vertex["production_vertex_table_candidate_exported"],
        "symbolic_4d_lagrangian_assembly_ledger_exported": lagrangian["symbolic_4d_lagrangian_assembly_ledger_exported"],
        "vertex_readiness_matrix_exported": readiness["vertex_readiness_matrix_exported"],
        "feynrules_export_blocker_table_exported": blockers["feynrules_export_blocker_table_exported"],
        "runtime_parameter_dependency_table_exported": runtime["runtime_parameter_dependency_table_exported"],
        "canonical_production_basis_preserved": True,
        "interface_normalization_gate_cleared": True,
        "production_vertex_table_complete": False,
        "mass_width_scheme_complete_for_pure_no_fit": False,
        "runtime_mass_width_policy_defined": True,
        "renormalization_scheme_complete": False,
        **readiness_false(),
        **guardrails(),
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "remaining_blockers": [
            "complete 4D Lagrangian",
            "production vertex table",
            "mass-width closure for BHSM_PURE_NOFIT",
            "renormalization closure",
            "FeynRules export",
            "loadable UFO model",
            "MadGraph validation",
            "LHE/HepMC generation",
            "Athena/CMSSW integration",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-G exports a candidate production vertex table and "
            "symbolic 4D Lagrangian assembly ledger in the canonical production "
            "basis. CKM/PMNS charged-current targets are structurally identified "
            "using BHSM-derived mixing sources, while charged boundary, neutral, "
            "and CP holonomy vertices remain blocked by explicit missing "
            "interaction/basis attachments. This is not production FeynRules/UFO readiness."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BHSM Phase Three-G gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

