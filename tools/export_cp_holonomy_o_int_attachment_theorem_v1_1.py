from __future__ import annotations

import argparse
import json
from pathlib import Path

from phase_three_i_common import guardrails, load_phase_three_i_inputs, source_artifact_list, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json"


def build_payload() -> dict[str, object]:
    inputs = load_phase_three_i_inputs()
    prior = inputs["cp_holonomy_attachment_resolution_attempt"]
    return {
        "artifact": "BHSM_cp_holonomy_o_int_attachment_theorem_v1_1",
        "release_basis": "v1.0.1",
        "phase": "PHASE_THREE_I_INTERACTION_THEOREM_CLOSURE",
        "theorem_name": "CP holonomy O_int attachment theorem",
        "theorem_status": "OPEN_EXACT_MISSING_THEOREM",
        "prior_blocker_status": prior["attachment_resolution_status"],
        "delta_BH": prior["delta_BH"],
        "holonomy_source": prior["holonomy_source"],
        "candidate_O_int_symbol": "O_int",
        "candidate_O_int_expression": "undefined pending standalone CP interaction attachment theorem",
        "candidate_O_int_interpretation": (
            "The standalone CP holonomy source exp(i delta_BH) becomes a production interaction "
            "only after O_int specifies field content, Lorentz structure, gauge structure, and "
            "coupling placement."
        ),
        "source_artifacts_checked": source_artifact_list(),
        "derived_from_repo_artifact": False,
        "derived_conditional_from_author_axiom": False,
        "standard_target_convention_used": False,
        "attached_to_CKM_PMNS_mixing": True,
        "standalone_attachment_defined": False,
        "affected_vertex_family": "cp_holonomy_phase_attachment",
        "promotes_standalone_cp_vertex": False,
        "promotion_status": "FORBIDDEN_TO_PROMOTE_WITHOUT_NEW_THEOREM",
        "missing_if_open": (
            "standalone interaction operator O_int with field content, Lorentz structure, "
            "gauge representation, and coupling placement"
        ),
        "forbidden_promotions": [
            "standalone_cp_holonomy_vertex_to_feynrules_ready",
            "general_cp_violating_lagrangian_complete",
            "O_int_defined_by_delta_BH_alone",
        ],
        "feynrules_ready": False,
        "ufo_ready": False,
        "notes": (
            "delta_BH remains partially attached through CKM/PMNS mixing sources. That does not "
            "define a standalone CP interaction vertex."
        ),
        **guardrails(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Phase Three-I CP O_int theorem attempt.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    write_json(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

