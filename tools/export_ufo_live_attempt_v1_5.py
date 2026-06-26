from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_m_common import ROOT, common_payload, enabled_model_path, load_required, ufo_output_directory, write_json


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_ufo_export_live_attempt_v1_5.json"


def build_payload() -> dict:
    validation = load_required("artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json")
    can_attempt = validation["feynrules_syntax_validated"] and validation["feynrules_model_load_validated"]
    # Deliberately do not perform the export here. A real export must be run by
    # the local wrapper in a Mathematica/FeynRules environment and then recorded.
    return {
        **common_payload(),
        "ufo_export_attempted": False,
        "ufo_export_passed": False,
        "input_feynrules_model": enabled_model_path(),
        "output_ufo_directory": ufo_output_directory(),
        "export_command": (
            "python scripts/feynrules/run_ufo_export_if_validated.py"
            if can_attempt
            else "not_run"
        ),
        "export_log_path": (
            "runs/feynrules_validation/ufo_export.log"
            if can_attempt
            else "not_created"
        ),
        "ufo_directory_created": False,
        "required_ufo_files_present": False,
        "ufo_loadability_tested": False,
        "ufo_loadability_passed": False,
        "failure_reason_if_any": (
            "not attempted by repository exporter; run local wrapper after validation"
            if can_attempt
            else "FeynRules validation gates did not pass"
        ),
        "notes": [
            "UFO export may be attempted only after live FeynRules validation passes.",
            "This artifact records the gate decision; it does not fabricate UFO files.",
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

