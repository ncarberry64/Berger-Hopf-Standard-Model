"""Apply the retained bordered-hard-inverse theorem to the exact cone."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import certify_n12_gate7_exact_affine_center_boundary_cluster_spectrum as spectrum  # noqa: E402
import certify_n12_gate7_exact_affine_center_selected_projector_graph as projector  # noqa: E402
import certify_n12_gate7_recentered_cone_bordered_hard_inverse as retained  # noqa: E402


RESULT = spectrum.BASE / (
    "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_HARD_INVERSE.json"
)
retained.SPECTRUM = spectrum.RESULT
retained.PROJECTOR = projector.RESULT
retained.RESULT = RESULT


def main() -> None:
    payload = retained.build_payload()
    payload["artifact"] = (
        "BHSM_N12_GATE7_EXACT_AFFINE_CENTER_BORDERED_HARD_INVERSE"
    )
    if payload["validation_passed"]:
        payload["status"] = (
            "ALL_EXACT_AFFINE_CENTER_CONE_BORDERED_HARD_INVERSES_CERTIFIED"
        )
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
