"""Replay the retained second-variation majorant on the exact cone."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as exact_cone  # noqa: E402
import certify_n12_gate7_exact_affine_center_selected_projector_graph as exact_projector  # noqa: E402
import certify_n12_gate7_exact_affine_center_bordered_hard_inverse as exact_inverse  # noqa: E402
import certify_n12_gate7_exact_affine_center_bordered_rhs_response as exact_response  # noqa: E402
import certify_n12_gate7_exact_affine_center_bordered_response_first_variation as exact_first  # noqa: E402
import certify_n12_gate7_recentered_cone_bordered_response_second_variation as retained  # noqa: E402


RESULT = exact_cone.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_SECOND_VARIATION.json"
)
retained.FIRST = exact_first.RESULT
retained.RESPONSE = exact_response.RESULT
retained.PROJECTOR = exact_projector.RESULT
retained.INVERSE = exact_inverse.RESULT
retained.RESULT = RESULT


def main() -> None:
    payload = retained.build_payload()
    first_payload = json.loads(exact_first.RESULT.read_text(encoding="utf-8"))
    response_payload = json.loads(exact_response.RESULT.read_text(encoding="utf-8"))
    first_keys = [
        (
            int(row["seam"]), int(row["local_index"]),
            int(row["parent_local_index"]), int(row["child_within_parent"]),
            tuple(row["action_interval"]),
        )
        for row in first_payload["rows"]
    ]
    response_keys = [
        (
            int(row["seam"]), int(row["local_index"]),
            int(row["parent_local_index"]), int(row["child_within_parent"]),
            tuple(row["action_interval"]),
        )
        for row in response_payload["rows"]
    ]
    payload["validation"].pop(
        "identical_24072_cell_zero_first_second_response_cover_consumed",
        None,
    )
    payload["validation"][
        "identical_final_exact_adaptive_zero_first_second_response_cover_consumed"
    ] = bool(
        first_keys == response_keys
        and len(first_keys) == int(response_payload["mesh"]["cells"])
        and len(first_keys) > 0
    )
    payload["validation_passed"] = all(payload["validation"].values())
    payload["artifact"] = (
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_SECOND_VARIATION"
    )
    if payload["validation_passed"]:
        payload["status"] = (
            "EXACT_AFFINE_CENTER_GATE7_CONE_COMPLETE_BORDERED_RESPONSE_SECOND_"
            "VARIATION_MAJORANT_CERTIFIED"
        )
        payload["exact_next_dependency"] = (
            "COMPOSE_THE_CERTIFIED_EXACT_CENTER_RESPONSE_VARIATIONS_WITH_THE_"
            "OUTWARD_CORRELATED_CAUSAL_GREEN_REMAINDERS_AND_CLOSE_THE_FINAL_Z2"
        )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "mesh": payload["mesh"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
        "exact_next_dependency": payload["exact_next_dependency"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
