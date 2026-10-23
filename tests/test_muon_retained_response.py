"""Focused import checks; retained controls do not certify physical admission.

No background, ancestor response or normal-graph Hessian is recomputed here.
"""
from __future__ import annotations

import os
import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.muon_baton_zoo_original_validation import independent_original_maxwell_weak
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_intrinsic_higgs_weak_action import higgs_action
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.retained_response import action_magnetic_kernel as magnetic
from bhsm.interface.retained_response import build_higgs_response as higgs
from bhsm.interface.retained_response import field_spin_connection as field
from bhsm.interface.retained_response import forced_canonical_source as forced
from bhsm.interface.retained_response import port_response
from bhsm.interface.retained_response.compatible_source import haar_rule, scalar_values
from bhsm.interface.retained_response.finite_time_response import full18_point
from bhsm.interface.retained_response.retained_magnetic_application import FRAME, wall_data


ROOT = Path(os.environ.get('BHSM_RETAINED_RESPONSE_TEST_ROOT', Path(__file__).resolve().parents[1]))
DATA = ROOT/'artifacts/muon_retained_response_20261018'
SAVED = DATA/'supplied'
SIDES = ('incoming', 'outgoing')


def load(path):
    with np.load(path, allow_pickle=False) as source:
        return {name: source[name] for name in source.files}


def maxabs(value):
    return float(np.max(np.abs(value)))


@pytest.mark.parametrize('side', SIDES)
def test_retained_material_clock_and_geometry_agree_with_live_owners(side):
    """Checks raw268 material At, spatial frame and induced lapse together."""
    for label in ('lo', 'q000', 'q001', 'q002', 'q003', 'hi'):
        raw = load(DATA/'inputs'/f'{side}_{label}.npz')['raw']
        wall, point, generators, _ = full18_point(raw)
        geometry = intrinsic_m4_weight_jet(12, raw[:37], raw[37:74], raw[74:98],
            source_value=raw[98], source_rate=raw[99])
        np.testing.assert_allclose(wall['lapse'], geometry['induced_lapse'].value, atol=4e-15, rtol=0)
        np.testing.assert_allclose(wall['R4'], geometry['R4'].value, atol=4e-15, rtol=0)
        connection = np.einsum('fc,cij->fij', wall['connection'][[0, 2, 3, 4]], generators)
        connection[0] /= wall['lapse']
        owned = canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
            spatial_derivative_map=np.zeros((1, 3, 18, 18)),
            H=(raw[260:262]+1j*raw[262:264])[None], R4=wall['R4'],
            gauge_connection=connection[None])
        np.testing.assert_allclose(point, wall['lapse']*owned['hamiltonian_map'][0], atol=5e-14, rtol=0)


@pytest.mark.parametrize('side', SIDES)
def test_signed_higgs_action_matches_live_owner_with_cap_normalization(side):
    """Includes mixed field products, temporal trace and real-H normalization."""
    raw = load(DATA/'inputs'/f'{side}_q001.npz')['raw']
    wall = wall_data(raw)
    points, weights = higgs.rule24()
    y = 2*points
    dy = 2*np.einsum('aij,pj->pai', FRAME, points)
    q = .001*np.sin(np.arange(80)+.31)
    qd = .001*np.cos(np.arange(80)+.17)
    hr = raw[260:264][None]+y@q[:16].reshape(4, 4).T
    htr = raw[264:268][None]+y@qd[:16].reshape(4, 4).T
    hsr = np.einsum('pah,ih->pai', dy, q[:16].reshape(4, 4))
    H = hr[:, :2]+1j*hr[:, 2:]
    ordinary = np.concatenate(((htr[:, :2]+1j*htr[:, 2:])[:, None],
        hsr[:, :, :2]+1j*hsr[:, :, 2:]), axis=1)
    gauge = wall['connection'][[0, 2, 3, 4]][None]+np.einsum('ph,fch->pfc', y, q[16:].reshape(4, 4, 4))
    generators = higgs_u2_real_representation()['complex_generators']
    omega = np.einsum('pfc,cij->pfij', gauge, generators)
    DH = ordinary+np.einsum('pfij,pj->pfi', omega, H)
    n, r = wall['lapse'], wall['R4']
    owned = higgs_action(quadrature=higgs.C_ORBIT*weights,
        kinetic_density=np.diag([r**3/n, -n*r, -n*r, -n*r])[None],
        volume_density=n*r**3, H=H, DH=DH, J=np.zeros_like(H),
        lambda_H=higgs.LAM, nu_squared=higgs.NU2)
    # This zero J is the classical bosonic-body comparison; no quantum load is selected.
    assert owned == pytest.approx(higgs.literal_action(raw, q, qd), abs=5e-14, rel=0)


def test_complex_maxwell_action_and_hessian_use_original_analytic_pairing():
    rng = np.random.default_rng(20261018)
    def make_field():
        def sample(shape):
            return .1*(rng.normal(size=shape)+.2j*rng.normal(size=shape))
        return magnetic.FieldJet(sample((3, 5, 4)), sample((3, 5, 4)),
            sample((3, 5, 4)), sample((3, 3, 5, 4)))
    base, u, v = make_field(), make_field(), make_field()
    densities = np.array([[1.1, .9, 1.3, 1.1*.9/1.3, .07],
        [1.3, 1.2, 1.4, 1.3*1.2/1.4, -.03], [.8, .7, .9, .8*.7/.9, .09]])
    weights = np.array([.2, .3, .5])
    def original(offset):
        a = base.plus(u, offset)
        return independent_original_maxwell_weak(connection=a.value,
            time_derivative=a.time, radial_derivative=a.radial, angular_derivative=a.angular,
            tests=v.value[:, None], tests_time=v.time[:, None], tests_radial=v.radial[:, None],
            tests_angular=v.angular[:, None], metric_densities=densities, quadrature=weights)
    step = .125
    derivative = (-original(2*step)['original_weak_rows']+8*original(step)['original_weak_rows']
        -8*original(-step)['original_weak_rows']+original(-2*step)['original_weak_rows'])/(12*step)
    np.testing.assert_allclose(weights@magnetic.local_action(base, densities),
        original(0)['original_action_value'], atol=2e-13, rtol=0)
    np.testing.assert_allclose(weights@magnetic.local_hessian(base, u, v, densities),
        derivative, atol=2e-13, rtol=0)
    assert not original(0)['analytic_components_conjugated']


@pytest.mark.parametrize('side', SIDES)
def test_field_vertices_are_live_local_hamiltonian_insertions(side):
    """Independent Haar projection of the live full18 owner checks all80 vertices."""
    path = field.OpenFieldPath(side)
    s = .31
    direction = .01*np.sin(np.arange(166)+.23)
    gauge, real_higgs = path.original_fields(s)
    gauge, real_higgs = gauge@direction, real_higgs@direction
    sg, weights, points = haar_rule(7)
    phi = scalar_values(sg, 2)
    y = 2*points
    g = np.einsum('ph,fch->pfc', y, gauge.reshape(4, 4, 4))
    h = y@real_higgs.reshape(4, 4).T
    H = h[:, :2]+1j*h[:, 2:]
    n = float(field.interpolate(path.s, path.N, s))
    r = float(field.interpolate(path.s, path.R4, s))
    generators = lepton_unit_trace_gauge_representation()['generators']
    connection = np.einsum('pfc,cij->pfij', g, generators)
    connection[:, 0] /= n
    common = dict(value_map=np.broadcast_to(np.eye(18), (len(points), 18, 18)),
        spatial_derivative_map=np.zeros((len(points), 3, 18, 18)), R4=r)
    changed = canonical_lepton_hamiltonian_maps(H=H, gauge_connection=connection, **common)
    reference = canonical_lepton_hamiltonian_maps(H=np.zeros_like(H),
        gauge_connection=np.zeros_like(connection), **common)
    local = n*(changed['hamiltonian_map']-reference['hamiltonian_map'])
    ids = np.array([2, 3, 8, 9, 14, 15])
    local = local[:, ids][:, :, ids]
    projected = np.einsum('p,pt,pij,ps->tisj', weights, phi.conj(), local, phi).reshape(84, 84)
    actual = path.insertion(s, direction)
    np.testing.assert_allclose(actual, projected, atol=3e-11, rtol=2e-14)
    assert maxabs(actual-actual.conj().T) < 2e-12


@pytest.mark.parametrize('side', SIDES)
def test_saved_magnetic_gauge_columns_already_include_direct_insertion(side):
    saved = load(SAVED/f'{side}_spin_response.npz')
    direct = load(DATA/'inputs'/f'{side}_direct_spin_result.npz')
    previous = direct['integrated_insertion'].reshape(6, 84, 84)[:, :, :30]
    np.testing.assert_allclose(saved['J_gauge'][160:], previous, atol=2e-19, rtol=0)
    assert maxabs(previous) > 1e-7
    # Adding the direct response would create this same nonzero duplicate.
    total = saved['J_gauge'][160:]+saved['J_Higgs'][160:]
    np.testing.assert_allclose((total+previous)-total, previous, atol=2e-20, rtol=0)


@pytest.mark.parametrize('side', SIDES)
def test_saved_open_application_preserves_endpoints_and_conditional_maxwell_domain(side):
    coefficient = .02*np.sin(np.arange(574)+.31)
    rho = np.eye(30)/30
    result = field.apply_open_result(SAVED, side, coefficient, initial_density=rho)
    maps = load(SAVED/f'{side}_joint_open_response.npz')
    assert result['classical_final_variation'].shape == (440,)
    assert result['lepton_propagator_first'].shape == (84, 30)
    assert result['initial_space_spin_operator_first'].shape == (3, 30, 30)
    np.testing.assert_array_equal(maps['field_to_spin_input_indices'], np.arange(408, 574))
    np.testing.assert_allclose(result['known_wall_weak_variation']-result['known_wall_temporal_endpoint_variation'],
        maps['wall_Euler_map']@coefficient, atol=2e-14, rtol=0)
    assert maxabs(maps['wall_temporal_endpoint']) > 1e-7
    expected = np.trace(result['initial_space_spin_operator_first'], axis1=1, axis2=2).real/30
    np.testing.assert_allclose(result['finite_density_spin_expectation_first'], expected, atol=1e-16, rtol=0)
    maxwell_only = coefficient.copy()
    maxwell_only[408:] = 0
    fixed_wall = field.apply_open_result(SAVED, side, maxwell_only)
    assert not np.any(fixed_wall['lepton_propagator_first'])
    assert maxabs(fixed_wall['classical_final_variation']) > 0
    assert result['physical_wall_closed'] is False
    assert result['physical_muon_admitted'] is False


@pytest.mark.parametrize('density', [np.eye(29)/29, np.eye(30),
    np.diag(np.r_[-.1, 1.1, np.zeros(28)]),
    np.eye(30)/30+np.eye(30, k=1)*.1])
def test_finite_density_application_rejects_invalid_states(density):
    with pytest.raises(ValueError, match='density'):
        field.apply_open_result(SAVED, 'incoming', np.ones(574), initial_density=density)


@pytest.mark.parametrize('source', [np.zeros(573), np.zeros(574, complex),
    np.r_[np.nan, np.zeros(573)]])
def test_open_application_rejects_undeclared_or_nonfinite_source_coordinates(source):
    with pytest.raises(ValueError, match='574'):
        field.apply_open_result(SAVED, 'incoming', source)


@pytest.mark.parametrize('side', SIDES)
def test_normal_graph_is_separate_evaluated_branch_and_reuses_legacy_response(side):
    graph = load(DATA/'normal_graph'/f'{side}_graph_response.npz')
    scalar = load(DATA/'inputs'/f'{side}_higgs_response.npz')
    assert graph['final'].shape == (32, 174)
    assert graph['weak_wall'].shape == (142, 174)
    np.testing.assert_array_equal(graph['final'][:, :166], scalar['final'])
    np.testing.assert_array_equal(graph['stages'][:, :, :166], scalar['stages'])
    np.testing.assert_allclose(graph['weak_wall'][:134, :166], scalar['weak_wall'], atol=2e-15, rtol=0)
    np.testing.assert_allclose(graph['wall_euler'], graph['weak_wall']-graph['wall_temporal_endpoint'], atol=1e-18, rtol=0)
    residual = graph['graph_drive_stage_system']@graph['direct_graph_stages'].reshape(128, 8)-graph['graph_drive_rhs']
    assert maxabs(residual) < 2e-20
    assert maxabs(graph['final'][:, 166:]) > 1e-8
    assert maxabs(graph['area_weak_per_gamma'][134:, 166:]) > 1
    # Eight graph coefficients have no implicit slots in the fixed-geometry574 input.
    with pytest.raises(ValueError, match='574'):
        field.apply_open_result(SAVED, side, np.zeros(582))


def forced_control_form():
    """Constructed analytic control with nonzero Gauss/current momentum sources."""
    M = np.diag([0., 1.3, 1.2, 1.1, 1.4]).astype(complex)
    B = .01*np.arange(25).reshape(5, 5).astype(complex)
    B[:, 0] = 0
    B[0, 1:] += .02j
    K = np.diag([2., -.2, -.3, -.4, -.5]).astype(complex)
    K[0, 1:] = [.2, -.1, .15, .07]
    K[1:, 0] = K[0, 1:]
    return forced.Form(M, B, K, np.array([.3, .1j, .2, -.1, .05]),
        np.array([0., .11, -.09j, .07, .03]), .17)


def test_forced_canonical_momentum_equals_original_action_after_gauss_elimination():
    full = forced_control_form()
    schur = forced.forced_gauss_schur(full, 1)
    reduced = schur['form']
    x = np.array([.2, -.1j, .13, -.04])
    velocity = np.array([-.15, .07, .03j, .12])
    y = schur['At_value_map']@x+schur['At_velocity_map']@velocity+schur['At_source_value']
    q, qd = np.r_[y, x], np.r_[0., velocity]
    assert maxabs(full.position_gradient(q, qd)[:1]) < 2e-15
    np.testing.assert_allclose(reduced.action(x, velocity), full.action(q, qd), atol=2e-15, rtol=0)
    np.testing.assert_allclose(reduced.momentum(x, velocity), full.momentum(q, qd)[1:], atol=2e-15, rtol=0)
    assert maxabs(reduced.h) > .05
    rhs = forced.canonical_rhs(reduced, np.r_[x, full.momentum(q, qd)[1:]])
    np.testing.assert_allclose(rhs[:4], velocity, atol=2e-15, rtol=0)
    np.testing.assert_allclose(rhs[4:], full.position_gradient(q, qd)[1:], atol=2e-15, rtol=0)


def test_moving_lift_preserves_original_action_source_momentum_and_endpoint_pairing():
    form = forced.forced_gauss_schur(forced_control_form(), 1)['form']
    E = np.array([[1., 0.], [0., 1.], [.2, 0.], [0., -.1]])
    Ed = np.array([[0., .01], [-.02, 0.], [.03, .01], [.02, -.04]])
    w, wd = np.array([0., 0., .13, -.2]), np.array([.01, -.03, .02, .07])
    pulled = forced.moving_lift_pullback(form, E=E, E_dot=Ed, w=w, w_dot=wd)
    x, xd, test = np.array([.2, -.3j]), np.array([-.1j, .07]), np.array([.23, .04j])
    q, qd = E@x+w, Ed@x+E@xd+wd
    np.testing.assert_allclose(pulled.action(x, xd), form.action(q, qd), atol=2e-15, rtol=0)
    np.testing.assert_allclose(pulled.momentum(x, xd), E.T@form.momentum(q, qd), atol=2e-15, rtol=0)
    np.testing.assert_allclose(pulled.momentum(x, xd)@test,
        form.momentum(q, qd)@(E@test), atol=2e-15, rtol=0)
    assert maxabs(pulled.h) > .05


def test_gauss_layout_retains_wall_electric_ports_and_only_four_relative_gauge_fixes():
    ids = np.arange(320).reshape(4, 5, 4, 4)
    for gauge in ('interior', 'wall'):
        y, x, ports, fixed = port_response.layout(gauge)
        assert (len(y), len(x), len(ports), len(fixed)) == (48, 204, 64, 4)
        np.testing.assert_array_equal(np.intersect1d(y, ids[3, 0].ravel()), np.array([], dtype=int))
        assert set(ids[3, 0].ravel()).issubset(ports)
        assert not set(ids[3, 1].ravel()) & set(ports)
        assert not set(fixed) & set(ports)


def test_live_owner_change_rejects_cached_application(monkeypatch):
    metadata=json.loads((DATA/'inputs/PROVENANCE.json').read_text())
    owner=next(iter(metadata['live_owner_lf_sha256']))
    metadata['live_owner_lf_sha256'][owner]='0'*64
    monkeypatch.setattr(field.json,'loads',lambda value:metadata)
    with pytest.raises(ValueError,match='live owner changed'):
        field.verify_inputs()


def test_modified_evaluated_array_is_rejected_before_application(tmp_path):
    binding=json.loads((SAVED/'BINDING.json').read_text())
    name='incoming_joint_open_response.npz'
    binding['files']={name:binding['files'][name]}
    (tmp_path/name).write_bytes((SAVED/name).read_bytes()+b'changed')
    (tmp_path/'BINDING.json').write_text(json.dumps(binding))
    with pytest.raises(ValueError,match='evaluated result changed'):
        field.verify_application_result(tmp_path)
