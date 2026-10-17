"""Independent literal-action, source-rate and boundary Wick checks."""
import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import Jet
from bhsm.interface.muon_parent_maxwell_full_weak import full_maxwell_action_jet
from bhsm.interface.muon_intrinsic_higgs_weak_action import higgs_action
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_local_wick_action import (
    local_field_chart, local_field_direction_basis, local_analytic_action_jet,
    wick_local_data, wick_directional_images, compare_local_wick_application,
    wick_temporal_coefficient_jet,
    local_analytic_ghost_pairing, wick_canonical_gauge_higgs_rows,
    local_ghost_coefficient_matrix, wick_local_slot_rotation,
)


def fixture():
    rng = np.random.default_rng(419)
    data = {k:rng.normal(size=v)*.13 for k, v in local_field_chart()['shapes'].items()}
    data['densities'] = np.array([3., 5., 2., 7.5, .17])
    data['weights'] = np.array([2.3, 1.7, 3.1])
    images = {k:rng.normal(size=(3,)+v)*.07 for k, v in local_field_chart()['shapes'].items()}
    return data, images


def test_real_primitive_values_equal_existing_signed_action_owners():
    data, images = fixture()
    app = local_analytic_action_jet(data, images, lambda_H=.3, nu_squared_action=.7)
    e, r, d, k, beta = data['densities']
    row = {name:Jet.constant(value, 1) for name, value in zip(
        ('electric', 'radial', 'angular', 'electric_radial', 'shift'), (e, r, d, k, beta))}
    row.update(connection_lambda=Jet.constant(1., 1), lambda_tau=Jet.constant(0., 1),
               lambda_rho=Jet.constant(0., 1))
    owned = full_maxwell_action_jet(dict(rows=[row], coordinate_count=1, clock='coefficient test'), np.ones(1), np.ones(1),
        gauge=data['A'][None, None], gauge_tau=data['A_time'][None, None],
        gauge_rho=data['A_radial'][None, None], gauge_angular=data['A_angular'][None, None])
    np.testing.assert_allclose(app['maxwell']['value'], owned['value'], rtol=1e-14, atol=1e-14)
    T = higgs_u2_real_representation()['real_generators']
    cov = data['H_derivative'].copy()
    for mu in range(4):
        cov[mu] += np.einsum('c,cij,j->i', data['A'][0 if mu == 0 else mu+1], T, data['H'])
    H = data['H'][:2]+1j*data['H'][2:]
    DH = cov[:, :2]+1j*cov[:, 2:]
    J = data['J'][:2]+1j*data['J'][2:]
    wt, ws, wv = data['weights']
    scalar = higgs_action(quadrature=np.ones(1), kinetic_density=np.diag([wt, -ws, -ws, -ws]),
        volume_density=wv, H=H[None], DH=DH[None], J=J[None], lambda_H=.3, nu_squared=.7)
    np.testing.assert_allclose(app['higgs']['value'], scalar, rtol=1e-14, atol=1e-14)


def test_exact_curvature_DH_source_seagull_and_all_conormal_continuations():
    data, images = fixture()
    app = compare_local_wick_application(data, images, lambda_H=.3, nu_squared_action=.7)
    assert max(app['action_continuation_residuals'].values()) < 2e-14
    assert max(app['conormal_continuation_residuals'].values()) < 2e-14
    assert not app['positive_real_Euclidean_reference_is_this_continued_base']
    assert app['euclidean_coefficient_imaginary_norm'] > .1
    assert not app['physical_native_heat_or_Pauli_evaluated']


def test_full_nonlinear_mixed_action_jet_against_independent_value_differences():
    data, images = fixture()
    kw = dict(lambda_H=.3, nu_squared_action=.7)
    app = local_analytic_action_jet(data, images, **kw)
    zero = {k:np.zeros((1,)+v) for k, v in local_field_chart()['shapes'].items()}
    def value(s, t):
        changed = {k:v+s*images[k][0]+t*images[k][1] for k, v in data.items()}
        a = local_analytic_action_jet(changed, zero, **kw)
        return np.array([a[k]['value'] for k in ('maxwell', 'higgs')])
    expected = np.array([app[k]['second'][0, 1] for k in ('maxwell', 'higgs')])
    defects = []
    for h in (2e-3, 1e-3):
        fd = (value(h, h)-value(h, -h)-value(-h, h)+value(-h, -h))/(4*h*h)
        defects.append(np.linalg.norm(fd-expected))
    assert defects[1] < .3*defects[0]
    assert defects[1] < 2e-8


def test_time_indexed_source_images_and_temporal_coefficient_germ_are_rotated():
    data, images = fixture()
    rotated = wick_local_data(data); source = wick_directional_images(images)
    np.testing.assert_array_equal(rotated['A'][0], -1j*data['A'][0])
    np.testing.assert_array_equal(rotated['A_time'][0], -data['A_time'][0])
    np.testing.assert_array_equal(rotated['A_time'][1:], -1j*data['A_time'][1:])
    np.testing.assert_array_equal(source['A_time'][:, 0], -images['A_time'][:, 0])
    np.testing.assert_array_equal(source['H_derivative'][:, 0], -1j*images['H_derivative'][:, 0])
    germ = wick_temporal_coefficient_jet(np.array([2., 3.]), np.array([5., 7.]), np.array([11., 13.]))
    np.testing.assert_array_equal(germ['first'], [-5j, -7j])
    np.testing.assert_array_equal(germ['second'], [-11., -13.])


def test_full_local_basis_preserves_each_ordinary_derivative_and_coefficient_slot():
    data, _ = fixture(); basis = local_field_direction_basis()
    chart = local_field_chart()
    packed = np.concatenate([basis[k].reshape(chart['dimension'], -1) for k in chart['shapes']], axis=1)
    np.testing.assert_array_equal(packed, np.eye(chart['dimension']))
    app = compare_local_wick_application(data, basis, lambda_H=.3, nu_squared_action=.7)
    assert max(app['action_continuation_residuals'].values()) < 2e-14
    assert max(app['conormal_continuation_residuals'].values()) < 2e-14


def test_covariant_ghost_form_and_existing_oriented_canonical_rows_continue():
    data, images = fixture(); rng = np.random.default_rng(73)
    left, right = rng.normal(size=(2, 4)); ld, rd = rng.normal(size=(2, 5, 4))
    metric = np.array([2., 3., 5., data['densities'][-1]])
    original = local_analytic_ghost_pairing(data['A'], metric, left, ld, right, rd)
    ew = wick_local_data(data); em = metric.astype(complex); em[-1] *= -1j
    eld, erd = ld.astype(complex), rd.astype(complex); eld[0] *= -1j; erd[0] *= -1j
    continued = local_analytic_ghost_pairing(ew['A'], em, left, eld, right, erd, signature='euclidean')
    np.testing.assert_allclose(original, -continued, rtol=1e-14, atol=1e-14)
    app = compare_local_wick_application(data, images, lambda_H=.3, nu_squared_action=.7)
    l, e = app['lorentz'], app['euclidean']
    rows = wick_canonical_gauge_higgs_rows(data['A'], l['gauge_temporal_momentum']['value'],
        data['H'], l['scalar_temporal_momentum']['value'], np.array([1., 2., 3., 4.]))
    np.testing.assert_allclose(rows['gauge_momentum'], e['gauge_temporal_momentum']['value'], atol=1e-14)
    np.testing.assert_allclose(rows['H_momentum'], e['scalar_temporal_momentum']['value'], atol=1e-14)
    assert not rows['new_terminal_domain_selected']


def test_complete_ghost_coefficient_operator_rotates_with_its_time_domain_slots():
    data, _ = fixture(); metric = np.array([2., 3., 5., .17])
    L = local_ghost_coefficient_matrix(data['A'], metric)
    ew = wick_local_data(data); em = metric.astype(complex); em[-1] *= -1j
    E = local_ghost_coefficient_matrix(ew['A'], em, signature='euclidean')
    rotation = np.ones(24, complex); rotation[4:8] = -1j
    np.testing.assert_allclose(L, -rotation[:, None]*E*rotation[None, :], atol=2e-14)
    slots = wick_local_slot_rotation()
    assert slots.shape == (local_field_chart()['dimension'],)
    assert np.min(abs(slots)) == 1
