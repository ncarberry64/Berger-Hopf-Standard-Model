"""Same-action bindings and active Euler rows of the new endpoint backend."""
from functools import lru_cache

import numpy as np
import pytest

from bhsm.interface.muon_parent_mean_causal_action import mean_action_family, local_mean_action
from bhsm.interface.muon_parent_gauge_geometry_correction import (
    finite_common_iterate_at_time, compact_temporal_basis,
)
from bhsm.interface.muon_pointwise_full_field_action import (
    pointwise_full_field_action, pointwise_wall_gauge_conormal,
    coefficient_time_euler_application,
)


@lru_cache(maxsize=1)
def _bound():
    family = mean_action_family()
    u = family['length']*.625
    t = u-family['length']
    rep, c = family['representation'], family['coefficients']
    d = finite_common_iterate_at_time(t, c, rep, family['reference'])
    b, bt = compact_temporal_basis(np.array([t]), rep['length'])
    scalar = c[rep['scalar_start']:]
    H, Ht = b[0]*scalar[:4]+scalar[4:], bt[0]*scalar[:4]
    raw = np.r_[d['q'], d['qdot'], d['m'], d['normal'], d['normal_rate'],
                b[0]*c[62:122], bt[0]*c[62:122], H, Ht]
    new = pointwise_full_field_action(raw, rep,
        nu_squared_action=family['nu_squared_action'], surface_gamma=family['surface_gamma'])
    old = local_mean_action(u, family)
    return family, raw, new, old


def test_all_raw_first_and_second_action_derivatives_match_retained_literal_backend():
    _, _, new, old = _bound()
    assert new['value'] == old['value']
    np.testing.assert_allclose(new['raw_gradient'], old['raw_gradient'], rtol=2e-14, atol=1e-14)
    np.testing.assert_allclose(new['raw_hessian'], old['raw_hessian'], rtol=2e-14, atol=1e-13)
    np.testing.assert_allclose(new['hessian'], old['hessian'], rtol=2e-14, atol=1e-13)


def test_zero_independent_gauge_start_retains_active_gauge_euler_and_mixed_scalar_rows():
    family, raw, _, _ = _bound()
    raw = raw.copy()
    raw[100:220] = 0.
    raw[224:228] = 0.
    new = pointwise_full_field_action(raw, family['representation'],
                                     nu_squared_action=family['nu_squared_action'])
    assert np.linalg.norm(new['raw_gauge_value_cotangent']) > 1e-8
    assert np.linalg.norm(new['raw_hessian'][100:160, 220:224]) > 1e-8
    assert new['zero_independent_gauge_Euler_inferred'] is False
    assert new['multiplier_and_At_Gauss_rows_retained'] is True


def test_euler_application_retains_supplied_acceleration_and_multiplier_motion():
    _, _, new, _ = _bound()
    tangent = np.linspace(-.3, .2, 216)
    base = coefficient_time_euler_application(new, tangent)
    moved = tangent.copy()
    moved[90:180] += .13
    moved[180:] -= .21
    delta = coefficient_time_euler_application(new, moved)
    np.testing.assert_allclose(delta['dynamic_euler']-base['dynamic_euler'],
        -new['hessian'][90:180]@(moved-tangent), rtol=1e-10, atol=2e-11)
    np.testing.assert_array_equal(delta['algebraic_constraint'], new['constraint_rows'])


def test_missing_rates_or_unassigned_nu_are_not_silent_zeros():
    family, raw, _, _ = _bound()
    with pytest.raises(ValueError, match='explicit real'):
        pointwise_full_field_action(None, family['representation'], nu_squared_action=4.)
    with pytest.raises((ValueError, TypeError)):
        pointwise_full_field_action(raw, family['representation'], nu_squared_action=None)
    with pytest.raises(ValueError, match='tangent'):
        coefficient_time_euler_application(_bound()[2], None)


def test_natural_wall_contact_uses_trace_and_retains_nonzero_reaction():
    family, raw, _, _ = _bound()
    face = pointwise_wall_gauge_conormal(raw, family['representation'])
    labels = family['representation']['gauge_labels']
    interior = [j for j, label in enumerate(labels) if not label['wall_lift']]
    ar = [j for j, label in enumerate(labels) if label['field'] == 'Ar']
    np.testing.assert_array_equal(face['radial_action_covector'][interior], 0.)
    np.testing.assert_array_equal(face['radial_action_covector'][ar], 0.)
    assert np.linalg.norm(face['radial_action_covector']) > 1e-5
    assert face['radial_quadrature_reused_as_face'] is False
    assert face['imposed_zero_flux'] is False
