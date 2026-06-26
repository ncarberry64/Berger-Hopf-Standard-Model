from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_e_common import guardrails, load_phase_three_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_renormalization_scheme_candidate_v0_7.json"


def build_payload() -> dict[str, object]:
    load_phase_three_inputs()
    return {
        "artifact": "BHSM_renormalization_scheme_candidate_v0_7",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_E_NORMALIZATION_GAUGE_SCHEME",
        "renormalization_scheme_name": "BHSM_INTERFACE_RENORMALIZATION_SCHEME_CANDIDATE",
        "reference_scale_status": "OPEN",
        "gauge_coupling_running_status": "SCHEME_CONDITIONAL",
        "yukawa_running_status": "OPEN",
        "threshold_scheme_status": "OPEN",
        "counterterm_scheme_status": "OPEN",
        "common_scale_transport_status": (
            "common-scale transport exists as BHSM interface artifact; "
            "production renormalization scheme remains open"
        ),
        "beta_functions_implemented": False,
        "invented_thresholds": False,
        "source_artifacts": source_artifact_list(),
        "missing_items": [
            "reference scale",
            "gauge coupling running convention",
            "Yukawa running convention",
            "threshold scheme",
            "counterterm scheme",
            "validated production renormalization prescription",
        ],
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": "No beta functions or thresholds are invented in this candidate ledger.",
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-E renormalization scheme candidate.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

