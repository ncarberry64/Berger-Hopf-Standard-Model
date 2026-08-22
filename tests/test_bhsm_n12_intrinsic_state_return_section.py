import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_STATE_RETURN_SECTION_GATE.json"
)


def test_intrinsic_state_return_section_gate_fails_closed() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert payload["validation_passed"] is True
    assert payload["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["regular_level_set_audit"]["row_rank"] == 57
    assert payload["regular_level_set_audit"]["local_linearized_nullity"] == 139
    assert payload["physical_tangent_moduli"]["N12_child_tangent_dimension"] == 66
    assert payload["physical_tangent_moduli"][
        "normal_complement_is_a_physical_selector"
    ] is False
    assert payload["action_selection_status"][
        "one_intrinsic_physical_point_or_orbit_selected"
    ] is False
    assert payload["derived_first_return_section"]["map_executable"] is False
    assert "C_infinity" in payload["derived_first_return_section"]["map"]
    assert len(payload["derived_first_return_section"][
        "required_existing_properties_to_close"
    ]) == 5
    assert payload["derived_first_return_section"][
        "conditional_regular_map_theorem"
    ].startswith("PROVED_BY_THE_IMPLICIT_FUNCTION_THEOREM")
    assert payload["derived_first_return_section"][
        "new_clock_period_event_equation_constraint_or_gate_added"
    ] is False
    assert payload["prediction_frozen"] is False
    assert payload["held_out_comparison_performed"] is False
