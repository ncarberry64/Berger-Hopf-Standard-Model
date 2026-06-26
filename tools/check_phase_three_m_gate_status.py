from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_m_common import ROOT, common_payload, enabled_model_path, load_required, write_json


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_phase_three_m_gate_status_v1_5.json"


def build_payload() -> dict:
    validation = load_required("artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json")
    enablement = load_required("artifacts/BHSM_feynrules_model_enablement_decision_v1_5.json")
    ufo = load_required("artifacts/BHSM_ufo_export_live_attempt_v1_5.json")
    madgraph = load_required("artifacts/BHSM_madgraph_live_smoke_attempt_v1_5.json")
    enabled_file_exists = (ROOT / enabled_model_path()).exists()
    return {
        **common_payload(),
        "live_feynrules_validation_attempt_artifact_exported": True,
        "feynrules_model_enablement_decision_exported": True,
        "ufo_export_live_attempt_artifact_exported": True,
        "madgraph_live_smoke_attempt_artifact_exported": True,
        "mathematica_detected": validation["mathematica_detected"],
        "wolframscript_detected": validation["wolframscript_detected"],
        "feynrules_detected": validation["feynrules_detected"],
        "madgraph_detected": madgraph["madgraph_detected"],
        "minimal_feynrules_model_file_enabled": enabled_file_exists and enablement["enablement_performed"],
        "production_feynrules_file_exported": enabled_file_exists and enablement["enablement_performed"],
        "feynrules_live_validation_attempted": validation["live_validation_attempted"],
        "feynrules_syntax_validated": validation["feynrules_syntax_validated"],
        "feynrules_model_load_validated": validation["feynrules_model_load_validated"],
        "feynman_rules_generation_attempted": validation["feynman_rules_generation_attempted"],
        "feynman_rules_generation_passed": validation["feynman_rules_generation_passed"],
        "ufo_export_attempted": ufo["ufo_export_attempted"],
        "ufo_export_passed": ufo["ufo_export_passed"],
        "ufo_loadability_tested": ufo["ufo_loadability_tested"],
        "ufo_loadability_passed": ufo["ufo_loadability_passed"],
        "madgraph_smoke_test_attempted": madgraph["madgraph_smoke_test_attempted"],
        "madgraph_smoke_test_passed": madgraph["madgraph_process_generation_passed"],
        "lhe_generation_ready": madgraph["lhe_generated"],
        "hepmc_generation_ready": madgraph["hepmc_generated"],
        "athena_ready": False,
        "cmssw_ready": False,
        "remaining_blockers": [
            "Mathematica/FeynRules runtime" if not validation["mathematica_detected"] else "live FeynRules validation pass",
            "FeynRules package detection" if not validation["feynrules_detected"] else "FeynRules model load validation",
            "enabled production .fr file",
            "UFO export",
            "UFO loadability",
            "MadGraph smoke test",
            "LHE/HepMC event generation",
            "Athena/CMSSW boundary",
        ],
        "recommended_status_language": (
            "BHSM Phase Three-M exports live FeynRules validation, enablement, UFO export, and MadGraph smoke-test attempt artifacts. "
            "The local environment did not provide Mathematica/FeynRules/MadGraph execution, so the minimal FeynRules model remains disabled and no FeynRules/UFO/MadGraph readiness is claimed."
            if not validation["feynrules_syntax_validated"]
            else "BHSM Phase Three-M validates the bounded minimal collider-interface FeynRules subset under live Mathematica/FeynRules execution and enables the minimal .fr file. This validates only the bounded CKM/PMNS collider-interface subset, not the complete BHSM 4D Lagrangian or full UFO/MadGraph/event readiness unless those additional gates also pass."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    write_json(Path(args.output), build_payload())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

