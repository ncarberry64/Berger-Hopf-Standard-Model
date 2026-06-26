from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_m_common import ROOT, common_payload, load_required, preflight_by_component, ufo_output_directory, write_json


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_madgraph_live_smoke_attempt_v1_5.json"


def build_payload() -> dict:
    ufo = load_required("artifacts/BHSM_ufo_export_live_attempt_v1_5.json")
    madgraph_detected = preflight_by_component()["madgraph"]["detected"]
    can_attempt = ufo["ufo_export_passed"] and ufo["ufo_loadability_passed"] and madgraph_detected
    return {
        **common_payload(),
        "madgraph_smoke_test_attempted": False,
        "madgraph_detected": madgraph_detected,
        "requires_loadable_ufo": True,
        "ufo_loadability_passed": ufo["ufo_loadability_passed"],
        "input_ufo_directory": ufo_output_directory(),
        "mg5_script_path": "scripts/madgraph/import_bhsm_minimal_ufo_smoke.mg5",
        "planned_processes": ["u d~ > w+", "e+ ve > w+"],
        "actual_processes_attempted": [],
        "madgraph_command": (
            "python scripts/madgraph/run_minimal_ufo_smoke_if_available.py"
            if can_attempt
            else "not_run"
        ),
        "madgraph_log_path": (
            "runs/madgraph_smoke/minimal_ufo_smoke.log"
            if can_attempt
            else "not_created"
        ),
        "madgraph_import_passed": False,
        "madgraph_process_generation_passed": False,
        "lhe_generated": False,
        "hepmc_generated": False,
        "failure_reason_if_any": (
            "not attempted by repository exporter; run local wrapper after UFO loadability passes"
            if can_attempt
            else "UFO export/loadability and/or MadGraph detection gates did not pass"
        ),
        "notes": [
            "MadGraph smoke testing may be attempted only after UFO export and loadability pass.",
            "No fake event outputs are generated.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    write_json(Path(args.output), build_payload())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

