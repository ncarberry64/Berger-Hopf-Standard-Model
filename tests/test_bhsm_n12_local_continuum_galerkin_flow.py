import json
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)


def test_local_continuum_galerkin_flow_is_certified_and_scoped() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    result = payload["scientific_result"]
    assert result["unique_local_continuum_retained_child_flow_exists"] is True
    assert result["nested_Galerkin_flows_are_Cauchy_in_XE_on_interval"] is True
    assert result["global_continuation_or_return_proved"] is False
    bounds = payload["directed_decimal_bounds"]
    assert Decimal(bounds["total_action_ball_radius_use_upper"]) < Decimal(
        bounds["existing_action_ball_radius"]
    )
    assert payload["prediction_frozen"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
