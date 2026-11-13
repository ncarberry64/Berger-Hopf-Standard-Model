"""Exact profile/overlap derivatives, separate from physical operator tests."""
from bhsm.interface.muon_eta_profile_attachment import (
    exact_profile_residuals, probability_pullback_residuals,
)


def test_adopted_normal_action_and_its_profile_derivative():
    residuals = exact_profile_residuals()
    assert residuals["normal_zero_mode_identity"] == 0
    assert residuals["normal_mass_profile_tangent"] == 0
    assert residuals["finite_normal_mass_deformation"] == 0


def test_unit_normalization_retains_the_overlap_cotangent():
    residuals = exact_profile_residuals()
    assert residuals["normalized_mode_tangent"] == 0
    assert residuals["actual_overlap_functional_kernel"] == 0


def test_probability_transport_is_distinct_from_scalar_field_pullback():
    residuals = probability_pullback_residuals()
    assert residuals["static_density_jacobian_term"] == 0
    assert residuals["join_density_jacobian_and_cosine_terms"] == 0


def test_evaluated_daughter_curve_uses_outgoing_field_and_owned_metric():
    """Read the actual integration; do not execute it a second time."""
    import json
    from pathlib import Path
    import numpy as np
    base = Path(__file__).resolve().parents[1]/'artifacts/muon_eta_profile_attachment_20261003/replay_reference'
    result = json.loads((base/'result.json').read_text())
    with np.load(base/'daughter_collar_profile.npz') as a:
        assert np.array_equal(a['f_eta_current'], a['rho']/2)
        assert np.allclose(a['m_eta_current'], -a['rho_s']/2/np.tan(a['rho']/2), rtol=2e-15, atol=0)
        assert max(abs(a['normal_metric_norm']+1)) < 1e-10
        t0,t1 = result['cached_metric_time_range']
        assert min(a['tau']) >= t0 and max(a['tau']) <= t1
        assert min(a['rho']) >= 0 and max(a['rho']) <= np.pi/2
        assert max(abs(a['tau_s'][1:])) > 0
        assert not result['full_source_support_curve_computed']
    assert result['execution']['finite_collar_curve_integrations'] == 1
    assert result['execution']['old_replays'] == 0
