from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_k_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_k_gate_status_v1_3.json"


def build_payload() -> dict[str, object]:
    export = load_required("artifacts/BHSM_minimal_feynrules_model_export_attempt_v1_3.json")
    contract = load_required("artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json")
    smoke = load_required("artifacts/BHSM_madgraph_smoke_test_plan_v1_3.json")
    load_required("artifacts/BHSM_software_track_readiness_gates_v1_3.json")
    return {
        "artifact": "BHSM_phase_three_k_gate_status_v1_3",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_K_FEYNRULES_EXPORT_ATTEMPT",
        "minimal_feynrules_model_export_attempted": True,
        "minimal_feynrules_model_file_created": export["model_file_created"],
        "minimal_feynrules_model_enabled": export["model_file_enabled"],
        "minimal_feynrules_model_is_complete_bhsm": export["is_complete_bhsm_model"],
        "minimal_feynrules_model_excludes_unresolved_vertices": True,
        "production_feynrules_file_exported": export["production_feynrules_file_exported"],
        "feynrules_syntax_validated": False,
        "ufo_export_attempted": contract["ufo_export_attempted"],
        "ufo_export_passed": contract["ufo_export_passed"],
        "ufo_loadability_tested": contract["ufo_loadability_tested"],
        "ufo_loadability_passed": contract["ufo_loadability_passed"],
        "madgraph_smoke_test_planned": True,
        "madgraph_smoke_test_attempted": smoke["smoke_test_attempted"],
        "madgraph_smoke_test_passed": smoke["smoke_test_passed"],
        "lhe_generation_ready": False,
        "hepmc_generation_ready": False,
        "athena_ready": False,
        "cmssw_ready": False,
        "empirical_derivation_inputs_used": False,
        "empirical_runtime_inputs_allowed_in_collider_mode": True,
        "boundary_predictions_modified_by_runtime_inputs": False,
        "boundary_predictions_modified_by_comparison": False,
        "official_predictions_changed": False,
        "source_model_files_changed": False,
        "remaining_blockers": [
            "enabled validated FeynRules file",
            "FeynRules syntax validation",
            "UFO export",
            "UFO loadability test",
            "MadGraph import",
            "MadGraph smoke process",
            "LHE/HepMC generation",
            "Athena/CMSSW detector-software boundary",
            "complete BHSM 4D Lagrangian",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-K exports or attempts to export a bounded minimal collider-interface "
            "FeynRules model for the CKM/PMNS charged-current subset only. The file excludes "
            "unresolved charged-boundary, neutral-kernel, and standalone CP-holonomy vertices and "
            "is not the complete BHSM 4D Lagrangian. UFO/MadGraph/event readiness remains gated "
            "unless actually validated."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-K gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

