from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_g_common import guardrails, load_phase_three_g_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_feynrules_export_blocker_table_v0_9.json"


STATUSES = {
    "complete_particle_table": "PARTIAL_CANDIDATE",
    "complete_parameter_card": "PARTIAL_CANDIDATE",
    "mass_width_scheme": "RUNTIME_POLICY_DEFINED_PURE_NOFIT_OPEN",
    "renormalization_scheme": "OPEN",
    "gauge_fixing_scheme": "TARGET_CONVENTION_PARTIAL",
    "production_coupling_scheme": "SCHEME_CONDITIONAL",
    "complete_vertex_table": "CANDIDATE_INCOMPLETE",
    "neutrino_basis_and_scale": "OPEN",
    "X_ch_interaction_operator": "OPEN",
    "CP_interaction_attachment": "OPEN",
    "FeynRules_syntax_export": "NOT_STARTED",
    "UFO_loadability_test": "NOT_STARTED",
    "MadGraph_smoke_test": "NOT_STARTED",
}


def blocker(blocker_id: str, status: str) -> dict[str, object]:
    return {
        "blocker_id": blocker_id,
        "status": status,
        "blocks_feynrules": True,
        "blocks_ufo": True,
        "blocks_madgraph": True,
        "current_artifact_support": source_artifact_list(),
        "missing_item": blocker_id,
        "can_be_runtime_input": blocker_id in {"mass_width_scheme", "complete_parameter_card"},
        "can_be_no_fit_derivation": blocker_id not in {"FeynRules_syntax_export", "UFO_loadability_test", "MadGraph_smoke_test"},
        "notes": "Blocker is explicit; no production FeynRules/UFO readiness is claimed.",
    }


def build_payload() -> dict[str, object]:
    load_phase_three_g_inputs()
    return {
        "artifact": "BHSM_feynrules_export_blocker_table_v0_9",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_G_VERTEX_TABLE_LAGRANGIAN_CANDIDATE",
        "feynrules_export_blocker_table_exported": True,
        "blockers": [blocker(blocker_id, status) for blocker_id, status in STATUSES.items()],
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BHSM Phase Three-G FeynRules blocker table.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

