from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_l_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_l_gate_status_v1_4.json"


def build_payload() -> dict[str, object]:
    syntax = load_required("artifacts/BHSM_feynrules_syntax_contract_v1_4.json")
    runner = load_required("artifacts/BHSM_feynrules_export_runner_package_v1_4.json")
    preflight = load_required("artifacts/BHSM_software_environment_preflight_v1_4.json")
    ufo = load_required("artifacts/BHSM_ufo_export_runner_contract_v1_4.json")
    mg = load_required("artifacts/BHSM_madgraph_smoke_runner_contract_v1_4.json")
    entries = {entry["component"]: entry for entry in preflight["entries"]}
    mathematica_detected = entries["mathematica_kernel"]["detected"] or entries["wolframscript"]["detected"]
    return {
        "artifact": "BHSM_phase_three_l_gate_status_v1_4",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_L_FEYNRULES_SYNTAX_RUNNER",
        "feynrules_syntax_contract_exported": True,
        "feynrules_export_runner_package_exported": runner["runner_package_created"],
        "software_environment_preflight_exported": True,
        "ufo_export_runner_contract_exported": True,
        "madgraph_smoke_runner_contract_exported": True,
        "static_contract_checks_passed": syntax["static_contract_passed"],
        "mathematica_detected": mathematica_detected,
        "feynrules_detected": entries["feynrules"]["detected"],
        "madgraph_detected": entries["madgraph"]["detected"],
        "minimal_feynrules_model_file_enabled": syntax["model_file_enabled"],
        "production_feynrules_file_exported": False,
        "feynrules_syntax_validated": syntax["mathematica_syntax_checked"],
        "feynrules_model_load_validated": syntax["feynrules_load_checked"],
        "ufo_export_attempted": ufo["ufo_export_attempted"],
        "ufo_export_passed": ufo["ufo_export_passed"],
        "ufo_loadability_tested": ufo["ufo_loadability_tested"],
        "ufo_loadability_passed": ufo["ufo_loadability_passed"],
        "madgraph_smoke_test_attempted": mg["smoke_test_attempted"],
        "madgraph_smoke_test_passed": mg["smoke_test_passed"],
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
            "enable and validate BHSM_Minimal_Collider_Interface.fr",
            "Mathematica/FeynRules model load",
            "FeynRules Lagrangian validation",
            "UFO export",
            "UFO loadability test",
            "MadGraph smoke test",
            "LHE/HepMC event generation",
            "Athena/CMSSW boundary",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-L exports a FeynRules syntax contract, local FeynRules/UFO runner "
            "package, software environment preflight, and MadGraph smoke-test runner contract for "
            "the bounded minimal collider-interface subset. Static repository checks may pass, but "
            "FeynRules syntax validation, UFO export/loadability, and MadGraph readiness remain "
            "false unless actually executed in an environment with Mathematica, FeynRules, and MadGraph."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-L gate status.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

