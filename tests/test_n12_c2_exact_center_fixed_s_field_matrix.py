import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "artifacts/flagship_integration/BHSM_N12_C2_EXACT_CENTER_FIXED_S_FIELD_MATRIX.json"


def test_exact_center_fixed_s_field_matrix() -> None:
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["center_field"]["Delta"] > 0.0
    assert abs(payload["center_field"]["Dlambda_field"] - 1.0) < 1.0e-8
    assert payload["center_field"]["Delta_first_partial_action_norm"] > 0.0
    assert (
        payload["center_field"][
            "Delta_first_total_remainder_action_norm_upper"
        ]
        / payload["center_field"]["Delta_first_partial_action_norm"]
        < 2.8e-3
    )
    assert "CLOSED_EUCLIDEAN_BALL" in payload["center_field"][
        "Delta_first_signed_center_ball"
    ]
    assert payload["comparison"]["matrix_to_scalar_ratio"] < 1.0e-8
    assert payload["fixed_descriptor_matrix"][
        "relative_second_variation_self_consistency"
    ] > 0.0
    assert payload["hindsight"]["obstruction_physical"] is False
    assert "INTERVAL_REMAINDER_OPEN" in payload["status"]
    assert payload["FLAGSHIP_READY"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
