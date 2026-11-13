"""Original-action reference-block tests; physical admission stays separate."""
from pathlib import Path
import numpy as np
import pytest

from bhsm.interface.muon_adopted_incoming_reference import (
    stationary_gauss_realization, solve_classical_reference_block,
    reference_endpoint_data,
    temporal_enrichment, stationary_parent_field_realization,
    reference_gauss_complements, static_field_maps,
)
from bhsm.interface.muon_parent_maxwell_full_weak import full_maxwell_weak_geometric_jets
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def raw():
    with np.load(ROOT/'artifacts/muon_retained_response_20261018/inputs/incoming_history.npz',allow_pickle=False) as z:
        return z['lo_raw_fields'].copy()


@pytest.fixture(scope='module')
def application(raw):
    return solve_classical_reference_block(raw,radial_points=24)


def test_original_material_Gauss_owner_agrees(raw):
    b = stationary_gauss_realization(raw,radial_points=16)
    original = b['evaluate'](b['initial'])
    n = len(b['rho'])
    independent = np.einsum('rp,pfc->rfc',b['basis'],raw[100:180].reshape(4,5,4))
    radial = np.einsum('rp,pfc->rfc',b['derivative'],raw[100:180].reshape(4,5,4))
    tests = np.zeros((n,16,1,5,4)); tests_rho = np.zeros_like(tests)
    for j in range(16):
        profile,channel = divmod(j,4)
        tests[:,j,0,0,channel] = b['basis'][:,profile]
        tests_rho[:,j,0,0,channel] = b['derivative'][:,profile]
    weak = full_maxwell_weak_geometric_jets(b['geometry'],b['radial_quadrature'],np.ones(1),
        gauge=independent[:,None],gauge_tau=np.zeros_like(independent[:,None]),
        gauge_rho=radial[:,None],gauge_angular=np.zeros((n,1,3,5,4)),
        tests=tests,tests_tau=np.zeros_like(tests),tests_rho=tests_rho,
        tests_angular=np.zeros((n,16,1,3,5,4)))
    expected = MAXWELL_TO_CAP*weak['weak']['values']
    expected[12:] += b['scalar_temporal_matrix']@b['initial'][12:]
    np.testing.assert_allclose(original['gradient'],expected,rtol=2e-12,atol=2e-21)


def test_nonlinear_block_converges_without_deleting_held_rows(raw,application):
    a = application
    assert a['status'] == 'CLASSICAL_INTERIOR_BLOCK_CONVERGED'
    assert len(a['active']) == 48
    assert len(a['realization']['frozen']) == 32
    assert np.max(abs(a['initial']['gradient'][a['active']])) > 10
    assert np.max(abs(a['final']['gradient'][a['active']])) < 2e-10
    assert np.max(abs(a['final']['gradient'][a['realization']['frozen']])) > .7
    np.testing.assert_array_equal(a['coefficients'][60:],raw[160:180])
    # All Ar values are retained as explicit fixed inputs, not relabeled
    # as the four central-Ar frame rows or discarded physical equations.
    ar = np.array([20*p+4+c for p in range(4) for c in range(4)])
    np.testing.assert_array_equal(a['coefficients'][ar],raw[100:180][ar])
    assert any(h.get('step_fraction') == .5 for h in a['history'])


def test_full_native_load_response_retained(application):
    a = application
    k = a['final']['hessian'][np.ix_(a['active'],a['active'])]
    np.testing.assert_allclose(k@a['unresolved_load_response'],-np.eye(48),atol=2e-13)
    assert np.linalg.norm(a['frozen_row_load_response']) > 0


def test_static_coordinates_keep_original_endpoint_momenta(application):
    e = reference_endpoint_data(application)
    assert np.max(abs(e['temporal_gauge_momentum'])) > 6
    assert np.max(abs(e['parent_outward_radial_gauge_conormal'])) > 6
    assert np.max(abs(e['scalar_real_temporal_momentum4'])) > 1e-10
    assert np.max(abs(e['wall_lift_reaction20']-e['parent_outward_radial_gauge_conormal'])) > 1


def test_real_chart_rejects_complex_source_without_projection(raw):
    with pytest.raises(ValueError,match='real incoming'):
        stationary_gauss_realization(raw.astype(complex)+1j*1e-30)


def test_regular_temporal_constant_is_admitted_without_changing_wall(raw):
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    rho = np.linspace(WALL/1000,WALL,29)
    p,pr = static_field_maps(rho,enrich_temporal=True)
    c = np.zeros(84); c[63] = c[83] = 1.
    np.testing.assert_allclose((p@c)[:,3],1.,atol=1e-15)
    np.testing.assert_allclose((pr@c)[:,3],0.,atol=1e-15)
    e,_ = temporal_enrichment(np.array([WALL]))
    np.testing.assert_array_equal(e,0.)


def test_enriched_block_preserves_all_old_tests_and_exposes_complement(raw):
    a = solve_classical_reference_block(raw,radial_points=24,enrich_temporal=True)
    assert a['status'] == 'CLASSICAL_INTERIOR_BLOCK_CONVERGED'
    assert len(a['active']) == 52
    assert len(a['realization']['frozen']) == 32
    old = stationary_parent_field_realization(raw,radial_points=24)
    np.testing.assert_allclose(a['initial']['gradient'][:80],old['evaluate'](old['initial'])['gradient'],atol=1e-13)
    np.testing.assert_array_equal(a['coefficients'][a['realization']['frozen']],old['initial'][a['realization']['frozen']])
    assert np.max(abs(a['final']['gradient'][a['active']])) < 2e-10
    complement = reference_gauss_complements(a)
    assert complement['weak_rows12'].shape == (12,)
    assert np.min(complement['test_Gauss_norm12']) > 0
    assert np.isfinite(complement['tested_dual_residual12']).all()


def test_nonzero_mixed_chart_matches_independent_original_weak_action(raw):
    from bhsm.interface.muon_nonlinear_n0_field_action import analytic_intrinsic_n0_jet
    from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
    r = stationary_parent_field_realization(raw,radial_points=8,enrich_temporal=True)
    c = r['initial']+.002*np.cos(np.arange(84))
    b = r['base']; n = len(b['rho'])
    p,pr = r['value_map'],r['radial_map']
    fields,radial = (p@c).reshape(n,1,5,4),(pr@c).reshape(n,1,5,4)
    tests = p.transpose(0,2,1).reshape(n,84,1,5,4)
    tests_r = pr.transpose(0,2,1).reshape(n,84,1,5,4)
    weak = full_maxwell_weak_geometric_jets(b['geometry'],b['radial_quadrature'],np.ones(1),
        gauge=fields,gauge_tau=np.zeros_like(fields),gauge_rho=radial,
        gauge_angular=np.zeros((n,1,3,5,4)),tests=tests,tests_tau=np.zeros_like(tests),
        tests_rho=tests_r,tests_angular=np.zeros((n,84,1,3,5,4)))
    expected = MAXWELL_TO_CAP*weak['weak']['values']
    m = intrinsic_m4_weight_jet(12,raw[:37],np.zeros(37),raw[74:98],source_value=raw[98],source_rate=0.)
    wall = c[60:80].reshape(5,4).copy()
    from bhsm.interface.muon_adopted_incoming_reference import M
    wall[2:] += M*(m['mechanical_connection_lambda'].value-1)
    scalar = analytic_intrinsic_n0_jet(wall,raw[260:264],np.zeros(4),
        [m[k].value for k in ('wT','wS','wV')],lambda_H=1.,nu_squared_action=1.)
    # Potential parameters affect scalar rows, not the gauge rows checked.
    expected[60:80] += scalar['gradient'][4:24].real
    np.testing.assert_allclose(r['evaluate'](c)['gradient'],expected,rtol=2e-12,atol=2e-13)
