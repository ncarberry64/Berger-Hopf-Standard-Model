import numpy as np

from bhsm.interface import aether_post_cut_nonround_lorentzian_cap_v15_48 as cap


def test_cap_action_contains_nonround_boundary_and_response_structure():
    contract = cap.lorentzian_cap_contract()
    assert contract["domain"].endswith("B4_times_S3")
    assert "GHY" in contract["spatial_action"]
    assert contract["child_scale"].endswith("-2*(v0-v1)")
    assert contract["new_continuous_coefficient"] is False


def test_reconstructed_data_embed_with_negative_child_orientation():
    initial = cap.projected_reconstructed_initial_data(points=500)
    assert abs(initial["canonical_energy"]) < 2e-7
    assert initial["initial_child_scale_velocity"] < 0.0
    assert initial["eta_Legendre_minimum"] > 0.0
    assert initial["Legendre_map_invertible"] is True
    assert np.all(np.isfinite(initial["accelerations"]))


def test_short_nonround_flow_enters_x_negative_cap():
    flow = cap.integrate_child_oriented_cap_flow(
        maximum_steps=10, points=55
    )
    assert flow["final_child_scale_x"] < 0.0
    assert flow["final_child_scale_velocity"] < 0.0
    assert flow["minimum_eta_Legendre"] > 0.0
    assert flow["turning_point_count"] == 0


def test_completion_payload_is_deterministic():
    payload = cap.completion_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["nonround_Lorentzian_cap_equations_derived"]
    assert payload["claim_boundary"]["persistent_particle_derived"] is False
    assert cap.deterministic_json(payload) == cap.deterministic_json(
        cap.completion_payload()
    )

