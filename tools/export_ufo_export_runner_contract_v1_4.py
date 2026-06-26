from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_l_common import guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_ufo_export_runner_contract_v1_4.json"


def build_payload() -> dict[str, object]:
    runner = load_required("artifacts/BHSM_feynrules_export_runner_package_v1_4.json")
    return {
        "artifact": "BHSM_ufo_export_runner_contract_v1_4",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_L_FEYNRULES_SYNTAX_RUNNER",
        "contract_name": "BHSM_MINIMAL_COLLIDER_INTERFACE_UFO_EXPORT_RUNNER_CONTRACT",
        "input_feynrules_model": runner["expected_enabled_model_file"],
        "output_ufo_directory": runner["expected_ufo_output_directory"],
        "mathematica_runner_script": runner["mathematica_script_path"],
        "export_command_template": "wolframscript -file scripts/feynrules/export_bhsm_minimal_to_ufo.m",
        "ufo_export_attempted": False,
        "ufo_export_passed": False,
        "ufo_directory_created": (ROOT / runner["expected_ufo_output_directory"]).exists(),
        "ufo_loadability_tested": False,
        "ufo_loadability_passed": False,
        "required_files_if_exported": [
            "__init__.py",
            "particles.py",
            "parameters.py",
            "couplings.py",
            "lorentz.py",
            "vertices.py",
        ],
        "missing_for_ufo": [
            "enabled validated .fr model file",
            "Mathematica/FeynRules execution",
            "successful WriteUFO run",
            "loadability test",
        ],
        "notes": "UFO export runner contract is present, but export was not attempted.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-L UFO export runner contract.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

