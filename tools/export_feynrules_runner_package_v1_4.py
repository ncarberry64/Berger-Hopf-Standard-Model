from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_l_common import disabled_model_path, guardrails, load_required, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_feynrules_export_runner_package_v1_4.json"


def build_payload() -> dict[str, object]:
    preflight = load_required("artifacts/BHSM_software_environment_preflight_v1_4.json")
    entries = {entry["component"]: entry for entry in preflight["entries"]}
    mathematica_detected = entries["mathematica_kernel"]["detected"] or entries["wolframscript"]["detected"]
    feynrules_detected = entries["feynrules"]["detected"]
    return {
        "artifact": "BHSM_feynrules_export_runner_package_v1_4",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_L_FEYNRULES_SYNTAX_RUNNER",
        "runner_package_created": True,
        "mathematica_script_path": "scripts/feynrules/export_bhsm_minimal_to_ufo.m",
        "model_check_script_path": "scripts/feynrules/check_bhsm_minimal_model.m",
        "input_model_file": disabled_model_path(),
        "expected_enabled_model_file": "models/feynrules/BHSM_Minimal_Collider_Interface.fr",
        "expected_ufo_output_directory": "models/ufo/BHSM_Minimal_Collider_Interface",
        "requires_mathematica": True,
        "requires_feynrules": True,
        "requires_feynarts_optional": True,
        "local_command_examples": [
            "wolframscript -file scripts/feynrules/check_bhsm_minimal_model.m",
            "wolframscript -file scripts/feynrules/export_bhsm_minimal_to_ufo.m",
        ],
        "export_attempted": False,
        "export_passed": False,
        "feynrules_version_detected": "not_detected" if not feynrules_detected else entries["feynrules"]["version"],
        "mathematica_version_detected": "not_detected" if not mathematica_detected else "detected_by_preflight",
        "missing_for_execution": [
            item
            for item, missing in [
                ("enabled validated .fr model file", True),
                ("Mathematica/FeynRules runtime unavailable", not (mathematica_detected and feynrules_detected)),
                ("FeynRules load validation", True),
            ]
            if missing
        ],
        "notes": "Runner scripts are local handoff scripts. They were not executed by Phase Three-L.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-L FeynRules runner package.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

