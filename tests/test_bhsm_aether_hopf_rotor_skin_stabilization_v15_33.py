import numpy as np

from bhsm.interface.aether_hopf_rotor_skin_stabilization_v15_33 import (
    charge_type_and_selection_audit,
    combined_nonlinear_stability_verdict,
    completion_payload,
    deterministic_json,
    fixed_eta_charge_curvature_theorem,
    minimal_missing_stabilizer_contract,
    sigma_weighted_rotor_inertia,
)


def test_event_degree_is_not_silently_used_as_canonical_charge():
    audit = charge_type_and_selection_audit()
    assert audit["event_degree_flux"]["integer_normalized"]
    assert audit["event_degree_flux"]["canonical_rotor_momentum"] is False
    assert audit["FR_parity_is_not_event_flux"]


def test_historical_fr_sector_remains_conditional():
    audit = charge_type_and_selection_audit()["historical_M8_FR_line"]
    assert audit["odd_degree_character"] == -1
    assert audit["physical_rotation_loop_identification_derived"] is False
    assert audit["collective_self_adjoint_domain_derived"] is False


def test_sigma_blind_charge_has_zero_curvature_in_fixed_eta_direction():
    theorem = fixed_eta_charge_curvature_theorem()
    assert theorem["first_sigma_variation"] == 0.0
    assert theorem["second_sigma_variation"] == 0.0
    assert theorem["v15_32_negative_direction_lifted"] is False


def test_retained_positive_g_rotor_weight_has_wrong_sign():
    result = sigma_weighted_rotor_inertia(points=16001)
    assert abs(result["S_first_derivative_at_seam"]) < 1e-10
    assert result["S_second_derivative_at_seam"] > 0.0
    assert result["seam_is_strict_inertia_minimum_for_positive_g"]
    assert result["g_positive_result"].startswith("STRICTLY_NEGATIVE")


def test_material_moment_runs_toward_vacuum_value():
    result = sigma_weighted_rotor_inertia(points=16001)
    rows = {row["shift"]: row["mean_sigma_squared"] for row in result["samples"]}
    assert rows[-4.0] > rows[0.0]
    assert rows[4.0] > rows[0.0]
    assert np.isclose(rows[-4.0], rows[4.0], atol=1e-10)


def test_combined_retained_charge_system_has_no_stable_child():
    result = combined_nonlinear_stability_verdict()
    assert result["skin_collective_second_variation"] < 0.0
    assert result["total_curvature_can_be_nonnegative_from_retained_charge"] is False
    assert result["stable_material_skin"] is False
    assert result["regular_persistent_encapsulated_child"] is False


def test_missing_stabilizer_is_classified_not_inserted():
    result = minimal_missing_stabilizer_contract()
    assert result["new_field_required"] is False
    assert result["new_action_structure_required"]
    assert result["inserted_in_this_campaign"] is False


def test_payload_and_json_are_deterministic():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
