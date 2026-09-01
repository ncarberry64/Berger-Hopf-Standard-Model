from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION.json"


def test_n12_c2_adaptive_ball_continuation() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    cover = payload["adaptive_cover"]
    assert cover["prior_total_segments"] == 451
    assert cover["additional_certified_segments"] > 0
    assert cover["total_certified_segments"] > 451
    assert cover["exhaustion_is_event_or_canonical_stop"] is False
    assert all(
        row["allocation_lower_necessity"]
        < row["allocation_selected_midpoint"]
        < row["allocation_feasible_upper"]
        and Decimal(row["physical_u_increment_decimal"]) > 0
        and row["proper_time_increment_interval"][0] > 0.0
        for row in cover["rows"]
    )
    assert payload["adjudication"]["fixed_half_allocation_blocker"] == "REMOVED"
    assert payload["claim_boundary"]["actual_later_event_or_canonical_stop"] == "OPEN"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
