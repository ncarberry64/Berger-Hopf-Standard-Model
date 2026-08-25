from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION.json"
)


def test_n12_c2_compensated_descriptor_continuation() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    cover = payload["compensated_cover"]
    assert cover["prior_total_segments"] == 436
    assert cover["additional_certified_segments"] > 0
    assert cover["total_certified_segments"] > 436
    assert cover["exhaustion_is_event_or_canonical_stop"] is False
    assert all(
        Decimal(row["signed_lambda_step_decimal"]) > 0
        and Decimal(row["physical_u_increment_decimal"]) > 0
        and row["proper_time_increment_interval"][0] > 0.0
        for row in cover["rows"]
    )
    assert payload["adjudication"]["binary64_signed_accumulator_blocker"] == "REMOVED"
    assert payload["claim_boundary"]["actual_later_event_or_canonical_stop"] == "OPEN"
    assert payload["claim_boundary"]["chord_03_authorized"] is False
