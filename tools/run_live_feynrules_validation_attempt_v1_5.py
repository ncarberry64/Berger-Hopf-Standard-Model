from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from phase_three_m_common import (
    ROOT,
    common_payload,
    disabled_model_path,
    environment_preflight_entries,
    excluded_vertices_confirmed,
    forbidden_content_confirmed_absent,
    preflight_by_component,
    write_json,
)


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_live_feynrules_validation_attempt_v1_5.json"


def build_payload() -> dict:
    entries = preflight_by_component()
    mathematica_detected = entries["mathematica_kernel"]["detected"]
    wolframscript_detected = entries["wolframscript"]["detected"]
    feynrules_detected = entries["feynrules"]["detected"]
    can_attempt = mathematica_detected and wolframscript_detected and feynrules_detected
    command = "python scripts/feynrules/run_live_feynrules_validation.py" if can_attempt else "not_run"
    log_path = "runs/feynrules_validation/live_feynrules_validation.log" if can_attempt else "not_created"
    payload = {
        **common_payload(),
        "environment_preflight": environment_preflight_entries(),
        "model_file_tested": disabled_model_path(),
        "model_scope": "BHSM_MINIMAL_COLLIDER_INTERFACE_ONLY",
        "is_complete_bhsm_model": False,
        "live_validation_attempted": False,
        "mathematica_detected": mathematica_detected,
        "wolframscript_detected": wolframscript_detected,
        "feynrules_detected": feynrules_detected,
        "validation_command": command,
        "validation_log_path": log_path,
        "mathematica_syntax_checked": False,
        "feynrules_package_loaded": False,
        "feynrules_model_loaded": False,
        "lagrangian_symbol_checked": False,
        "feynman_rules_generation_attempted": False,
        "feynman_rules_generation_passed": False,
        "feynrules_syntax_validated": False,
        "feynrules_model_load_validated": False,
        "failure_reason_if_any": "Mathematica/FeynRules runtime unavailable",
        "excluded_vertices_confirmed": excluded_vertices_confirmed(),
        "forbidden_content_confirmed_absent": forbidden_content_confirmed_absent(),
        "notes": [
            "Static contract checks are not live FeynRules validation.",
            "The disabled model is the committed source input.",
        ],
    }
    if can_attempt:
        result = subprocess.run(
            [sys.executable, "scripts/feynrules/run_live_feynrules_validation.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        # The wrapper writes a real log if execution occurs. Interpret only a zero
        # exit as live validation success; do not infer success from static text.
        passed = result.returncode == 0
        payload.update(
            {
                "live_validation_attempted": True,
                "mathematica_syntax_checked": passed,
                "feynrules_package_loaded": passed,
                "feynrules_model_loaded": passed,
                "lagrangian_symbol_checked": passed,
                "feynman_rules_generation_attempted": passed,
                "feynman_rules_generation_passed": passed,
                "feynrules_syntax_validated": passed,
                "feynrules_model_load_validated": passed,
                "failure_reason_if_any": "none" if passed else "Live FeynRules wrapper failed; inspect log",
            }
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    write_json(Path(args.output), build_payload())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

