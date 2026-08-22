import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_SINGULAR_EVENT_TEMPORAL_CHIRALITY.json"
)


def test_singular_event_orientation_is_action_owned_but_not_selected() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["validation_passed"] is True
    assert payload["physical_time"] == "ORIENTED_AND_FORWARD"
    assert payload["formal_reflection_is_gauge"] is False
    assert payload["ordinary_event_transport_correction"]["status"] == (
        "UNDEFINED_AT_THE_EXACT_EVENT_BECAUSE_D(E)_HAS_KERNEL_PSI"
    )
    assert payload["one_sided_action_identity"]["squared_limit"] == (
        "LIM_D_DT(LAMBDA^2)=2*C_PSI*B_PSI"
    )
    assert payload["refined_root_ball_enclosure"]["forcing_absolute_lower"] > 0.0
    assert payload["refined_root_ball_enclosure"]["cubic_absolute_lower"] > 0.0
    assert payload["center_and_cross_quadrature"]["96"]["hitting_product"] < 0.0
    assert payload["formal_reflection"]["hitting_product_reflected"] > 0.0
    conclusion = payload["event_to_child_conclusion"]
    assert conclusion["one_temporal_chirality_sector_action_selected"] is False
    assert conclusion["two_sectors_action_proved_physically_equivalent"] is False
    assert conclusion["two_sectors_quotiented"] is False

