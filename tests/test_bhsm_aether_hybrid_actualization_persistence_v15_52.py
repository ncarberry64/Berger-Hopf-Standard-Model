import numpy as np

from bhsm.interface import aether_hybrid_actualization_persistence_v15_52 as hybrid


def test_only_discrete_invariants_cross_actualization_event():
    result = hybrid.actualization_invariant_tuple()
    assert result["global_event_degree"] == 1
    assert result["orientation_branch"] == "child_x_negative"
    assert result["FR_parity"] == -1
    assert "metric" in result["not_transported"]
    assert "canonical_metric_momentum" in result["not_transported"]


def test_metric_erasing_reset_has_zero_physical_derivative():
    derivative = hybrid.physical_reset_jacobian()
    assert derivative.shape == (12, 12)
    assert np.count_nonzero(derivative) == 0
    result = hybrid.hybrid_monodromy()
    assert result["monodromy_rank"] == 0
    assert result["spectral_radius"] == 0.0
    assert result["continuous_geometric_cycle_asymptotically_stable"]
    assert result["FR_projective_multiplier"] == 1.0


def test_hybrid_cycle_returns_to_selected_constrained_state():
    payload = hybrid.completion_payload()
    assert payload["validation_passed"]
    assert payload["hybrid_cycle"]["hybrid_fixed_point"] == "P(z_star)=z_star"
    assert payload["claim_boundary"]["hybrid_event_relative_periodic_orbit_derived"]
    assert payload["claim_boundary"]["smooth_relative_periodic_orbit_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_payload_json_is_deterministic():
    payload = hybrid.completion_payload()
    assert hybrid.deterministic_json(payload) == hybrid.deterministic_json(
        hybrid.completion_payload()
    )
