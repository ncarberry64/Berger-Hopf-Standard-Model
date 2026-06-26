from __future__ import annotations

import argparse
from pathlib import Path

from phase_three_m_common import (
    ROOT,
    candidate_enabled_model_path,
    common_payload,
    disabled_model_path,
    enabled_model_path,
    load_required,
    write_json,
)


DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_feynrules_model_enablement_decision_v1_5.json"


def build_payload() -> dict:
    validation = load_required("artifacts/BHSM_live_feynrules_validation_attempt_v1_5.json")
    gates = {
        "feynrules_syntax_validated": validation["feynrules_syntax_validated"],
        "feynrules_model_load_validated": validation["feynrules_model_load_validated"],
        "lagrangian_symbol_checked": validation["lagrangian_symbol_checked"],
        "excluded_vertices_confirmed": validation["excluded_vertices_confirmed"],
        "forbidden_content_confirmed_absent": validation["forbidden_content_confirmed_absent"],
    }
    enablement_allowed = all(gates.values())
    return {
        **common_payload(),
        "disabled_model_path": disabled_model_path(),
        "candidate_enabled_model_path": candidate_enabled_model_path(),
        "enabled_model_path": enabled_model_path(),
        "enablement_attempted": True,
        "enablement_allowed": enablement_allowed,
        "enablement_performed": False,
        "enablement_reason": (
            "Live FeynRules validation gates passed; a future controlled enablement step may create the production .fr file."
            if enablement_allowed
            else "Live FeynRules validation did not pass; committed model remains disabled."
        ),
        "required_validation_gates": list(gates),
        "validation_gates_passed": [key for key, value in gates.items() if value],
        "validation_gates_failed": [key for key, value in gates.items() if not value],
        "model_scope": "BHSM_MINIMAL_COLLIDER_INTERFACE_ONLY",
        "is_complete_bhsm_model": False,
        "unresolved_vertices_excluded": validation["excluded_vertices_confirmed"],
        "notes": [
            "The enabled .fr file is not created by this exporter.",
            "Static checks alone never authorize enablement.",
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

