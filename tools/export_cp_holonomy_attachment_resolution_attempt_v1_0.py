from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_h_common import guardrails, load_phase_three_h_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_cp_holonomy_attachment_resolution_attempt_v1_0.json"


def build_payload() -> dict[str, object]:
    load_phase_three_h_inputs()
    return {
        "artifact": "BHSM_cp_holonomy_attachment_resolution_attempt_v1_0",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_H_BOUNDED_BLOCKER_RESOLUTION",
        "blocker_id": "CP_interaction_attachment",
        "blocker_name": "CP holonomy interaction attachment",
        "prior_status": "OPEN",
        "delta_BH": "pi/3",
        "holonomy_source": "CP_no_fit_holonomy_output_v1",
        "attachment_resolution_status": "PARTIALLY_RESOLVED_FOR_CKM_PMNS_MIXING_VERTICES",
        "source_artifacts_checked": source_artifact_list(),
        "affected_vertex_families": [
            "q_charged_current_CKM_BH",
            "lepton_charged_current_PMNS_BH",
            "cp_holonomy_phase_attachment",
        ],
        "promoted_vertex_families": [
            "q_charged_current_CKM_BH",
            "lepton_charged_current_PMNS_BH",
        ],
        "still_blocked_vertex_families": ["cp_holonomy_phase_attachment"],
        "missing_interaction_attachment_if_open": (
            "derive the standalone interaction operator O_int for "
            "G_raw * exp(i*delta_BH) * O_int + h.c."
        ),
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "delta_BH = pi/3 is already sourced in CKM/PMNS mixing artifacts, "
            "so CP attachment is partially resolved there. The standalone CP "
            "holonomy vertex remains blocked by missing O_int."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-H CP holonomy resolution attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

