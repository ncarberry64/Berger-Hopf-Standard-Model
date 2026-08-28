from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
)


def _load(name: str) -> dict:
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def test_quarter_step_common_frame_operands_share_the_selected_center() -> None:
    graph = _load(
        "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.json"
    )
    residual = _load(
        "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json"
    )
    first_hit = _load(
        "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json"
    )
    hybrid = _load(
        "BHSM_N12_GATE7_QUARTER_STEP_HYBRID_GRAPH_JACOBIAN_EQUIVALENCE_AUDIT.json"
    )
    assert graph["center"] == CENTER
    assert residual["construction"]["center"] == CENTER
    assert first_hit["center"] == CENTER
    assert CENTER in graph["inputs"]
    assert hybrid["center"] == CENTER
    assert hybrid["validation_passed"] is True


def test_reconnaissance_operands_are_not_promoted() -> None:
    graph = _load(
        "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.json"
    )
    residual = _load(
        "BHSM_N12_C2_STOP_QUARTER_STEP_RETAINED_DENSE_RESIDUAL_GAUSS12_RECONNAISSANCE.json"
    )
    first_hit = _load(
        "BHSM_N12_C2_STOP_QUARTER_STEP_DENSE_DESCRIPTOR_FIRST_HIT.json"
    )
    assert graph["validation_passed"] is False
    assert residual["validation_passed"] is False
    assert first_hit["validation_passed"] is True
    assert first_hit["claim_boundary"]["exact_history_first_hit"].startswith(
        "OPEN_UNTIL"
    )
