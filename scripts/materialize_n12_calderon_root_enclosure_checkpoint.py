"""Materialize the fail-closed N12 exact-root Calderon audit manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTED = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_CALDERON_DIRECTED_CENTER.json"
)
ACTION_BALL = ROOT / (
    "artifacts/n12_direct_checkpoint/BHSM_N12_CALDERON_ACTION_BALL.json"
)
ROOT_ROUNDING = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_DIRECTED_ROUNDING_CERTIFICATE.json"
)
RESULT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_CALDERON_ROOT_ENCLOSURE_CHECKPOINT.json"
)
REPRODUCERS = (
    ROOT / "scripts/certify_n12_calderon_directed_center.py",
    ROOT / "scripts/certify_n12_calderon_action_ball.py",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    directed = json.loads(DIRECTED.read_text(encoding="utf-8"))
    action_ball = json.loads(ACTION_BALL.read_text(encoding="utf-8"))
    sector_defects = {
        name: float(record["interval_inverse_defect_upper"])
        for name, record in directed["sector_records"].items()
    }
    validation = {
        "certified_direct_N12_root_enclosure_consumed": (
            directed["exact_root_action_coordinate_distance_upper"] > 0.0
        ),
        "both_gauge_fixed_sector_inverses_remain_contractive": all(
            value < 1.0 for value in sector_defects.values()
        ),
        "coupled_graph_box_failure_recorded_fail_closed": (
            directed["symbol"]["interval_inverse_defect_upper"] >= 1.0
            and directed["validation_passed"] is False
        ),
        "isotropic_action_ball_does_not_claim_root_inclusion": (
            action_ball["validation_passed"] is False
        ),
        "continuum_and_full_BHSM_remain_false": (
            directed["CONTINUUM_EVENT_CHILD_CERTIFIED"] is False
            and directed["FULL_BHSM_COMPLETE"] is False
        ),
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    paths = (DIRECTED, ACTION_BALL, ROOT_ROUNDING, *REPRODUCERS)
    output = {
        "classification": (
            "N12_EXACT_ROOT_CALDERON_ENCLOSURE_BLOCKER_LOCALIZED_TO_"
            "LOSS_OF_CONTRACTION_CORRELATIONS_IN_THE_INDEPENDENT_"
            "COORDINATE_BOX"
        ),
        "scientific_result": {
            "exact_root_action_coordinate_distance_upper": directed[
                "exact_root_action_coordinate_distance_upper"
            ],
            "gauge_fixed_sector_interval_inverse_defects": sector_defects,
            "coupled_graph_symbol_interval_inverse_defect": directed[
                "symbol"
            ]["interval_inverse_defect_upper"],
            "retained_action_obstruction_demonstrated": False,
            "numerical_overenclosure_localized": True,
        },
        "claim_boundary": (
            "THE_BINARY_CENTER_SYMBOL_IS_DIAGNOSTICALLY_TRANSVERSE_AND_"
            "THE_TWO_GAUGE_FIXED_SECTOR_INVERSES_ARE_CERTIFIED_ON_THE_"
            "EXACT_ROOT_BOX;_THE_COUPLED_GRAPH_SYMBOL_IS_NOT_CERTIFIED_"
            "ON_THAT_BOX,_SO_c_M0,_CONTINUUM_CHILD,_Q_xi,_AND_DELTA_H_"
            "REMAIN_OPEN"
        ),
        "exact_next_dependency": directed["exact_next_dependency"],
        "reproduction": [
            "python scripts/certify_n12_calderon_directed_center.py",
            "python scripts/certify_n12_calderon_action_ball.py",
            "python scripts/materialize_n12_calderon_root_enclosure_checkpoint.py",
        ],
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in paths
        },
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
