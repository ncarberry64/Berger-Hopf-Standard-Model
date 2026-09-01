import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"


def test_cancelled_fiber_continuation_is_certified() -> None:
    payload = json.loads((
        BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
    ).read_text(encoding="utf-8"))
    cover = payload["continuation"]
    assert payload["validation_passed"] is True
    assert cover["prior_total_segments"] == 1064
    assert cover["additional_certified_segments"] == 64
    assert Decimal(cover["final_signed_lambda_decimal"]) > 5 * Decimal(
        cover["initial_signed_lambda_decimal"]
    )
    assert cover["exhaustion_is_event_or_canonical_stop"] is False


def test_cancelled_first_box_has_strict_margins() -> None:
    payload = json.loads((
        BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION.json"
    ).read_text(encoding="utf-8"))
    row = payload["continuation"]["rows"][0]
    assert Decimal(row["signed_lambda_step_decimal"]) > Decimal("1e-22")
    assert row["hard_denominator_lower"] > 0.0
    assert row["Delta_lower"] > 0.0
    assert row["root_use_inside_selected_ball"] < row["selected_ball_radius"]


def test_center_matrix_stability_keeps_interval_claim_open() -> None:
    payload = json.loads((
        BASE / "BHSM_N12_C2_DESCRIPTOR_FIBER_CENTER_MATRIX_STABILITY.json"
    ).read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["difference_scales"]["complete_c_gradient_relative_defect"] < 0.02
    assert payload["difference_scales"]["tangent_matrix_relative_Frobenius_defect"] > 0.5
    assert payload["diagnosis"]["proof_authority"] == "CENTER_DIAGNOSTIC_ONLY"
    assert payload["FULL_BHSM_COMPLETE"] is False
