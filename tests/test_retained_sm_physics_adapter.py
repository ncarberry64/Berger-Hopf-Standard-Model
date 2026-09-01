from pathlib import Path

from bhsm.interface.retained_sm_physics_adapter import (
    load_retained_sm_component_match,
)


ROOT = Path(__file__).resolve().parents[1]


def retained_match():
    return load_retained_sm_component_match(
        ROOT / "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
        ROOT / "artifacts/BHSM_aether_common_gauge_hs_pushforward_v16_05.json",
        ROOT / "artifacts/BHSM_aether_cycle_scale_renormalization_v15_89.json",
    )


def test_retained_representation_and_response_components_match_without_promotion() -> None:
    result = retained_match()
    matched = result.matched_inputs()
    assert matched["faithful_gauge_group"] == "(SU3_times_Sp1_times_U1_Y)/Z6"
    assert matched["families"] == 3
    assert matched["one_family_complex_dimension"] == 16
    assert len(matched["allowed_yukawa_channels"]) == 4
    assert matched["gauge_response_sectors"] == ["SU2", "SU3", "U1"]
    assert matched["historical_centers_promoted"] is False


def test_exact_missing_action_inputs_are_not_filled_from_historical_components() -> None:
    blockers = retained_match().physical_engine_blockers(
        gate7_closed=False,
        current_background_attached=False,
        full_field_action_attached=False,
        universal_gf_scale_attached=True,
    )
    assert "Gate7_closed_background" in blockers
    assert "machine_readable_full_gauge_fermion_HS_action" in blockers
    assert "same_action_replacement_quantum_saddle" in blockers
    assert "action_selected_physical_HS_direction" in blockers
    assert "action_derived_Yukawa_matrices" in blockers
    assert "local_zero_momentum_gauge_couplings" in blockers
