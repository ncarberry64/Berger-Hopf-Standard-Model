"""Replay the retained first-variation theorem on the exact cone."""

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
import certify_n12_gate7_recentered_cone_bordered_response_first_variation as retained  # noqa: E402


RESULT = exact_cone.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_FIRST_VARIATION.json"
)
retained.cone = exact_cone.cone
retained.RESPONSE = exact_response.RESULT
retained.PROJECTOR = exact_projector.RESULT
retained.INVERSE = exact_inverse.RESULT
retained.RESULT = RESULT
retained._projector_rows.cache_clear()
retained._inverse_rows.cache_clear()


def main() -> None:
    payload = retained.build_payload()
    payload["artifact"] = (
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_RESPONSE_FIRST_VARIATION"
    )
    if payload["validation_passed"]:
        payload["status"] = (
            "EXACT_AFFINE_CENTER_GATE7_CONE_COMPLETE_BORDERED_RESPONSE_FIRST_"
            "VARIATION_CERTIFIED"
        )
    payload["inputs"].update({
        retained._relative(exact_cone.RESULT): retained._sha256(exact_cone.RESULT),
        retained._relative(Path(__file__).resolve()): retained._sha256(
            Path(__file__).resolve()
        ),
    })
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
