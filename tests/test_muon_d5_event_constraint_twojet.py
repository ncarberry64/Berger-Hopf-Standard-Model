"""Original E1 constraint curvature and unassigned KKT multiplier contacts."""
from pathlib import Path
import json

import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_d5_event_constraint_twojet import (
    CHART_SIZE, event_constraint_twojet, constraint_normal_stationarity_contact,
    known_action_normal_contacts,
)
from bhsm.interface.muon_d5_event_bundle_incidence import original_event_coefficients
from bhsm.interface.muon_d5_event_formation_constraints import (
    corrected_original_event_source_directions, proper_normal_coordinate_columns,
)
from bhsm.interface.muon_d5_event_normal_source_application import ProvisionalNormalSourceHistory
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_d5_spatial_bundle_application import (
    spatial_bundle_application, spatial_connection_row, cross_matrix,
)
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_parent_retarded_hypercharge import WALL


@pytest.fixture(scope='module')
def actual():
    root = Path(__file__).resolve().parents[1]
    folder = root/'artifacts/muon_retained_response_20261018/inputs'
    metadata = json.loads((folder/'history_metadata.json').read_bytes())
    histories = []
    for side in ('incoming', 'outgoing'):
        rows = metadata['sides'][side]
        with np.load(folder/(side+'_history.npz'), allow_pickle=False) as z:
            t = np.array([r['time'] for r in rows])
            x = np.array([z[r['label']+'_raw_fields'] for r in rows])
            xt = np.array([z[r['label']+'_raw_coordinate_time_derivative'] for r in rows])
        histories.append(recovered_export_history(root, side, t, x, xt)[0])
    with np.load(root/'artifacts/muon_d5_event_matching_20261019/formation_core/application.npz') as z:
        psi = z['provisional_normal_displacement_source_correction'].real
    raw = [h.value(0.)[0] for h in histories]
    corrected = [ProvisionalNormalSourceHistory(h, p).source(0.)[0] for h, p in zip(histories, psi)]
    coeff = [original_event_coefficients(h, 0., [WALL], side=side,
        directions=corrected_original_event_source_directions(h, dx-h.source(0.)[0], side=side))
        for h, side, dx in zip(histories, ('parent', 'child'), corrected)]
    spatial, _ = spatial_bundle_application(*coeff, histories[1])
    operands = histories[1].original_phase_operands
    geometry = np.array([raw[0][:100], raw[1][:100], operands['initial_pair'][0, :100],
        operands['reference_pair'][0, :100], operands['reference_pair'][1, :100]])
    independent = np.array([(h.gauge_basis([WALL])[0]@r[100:180]).reshape(5, 4)
        for h, r in zip(histories, raw)])
    jets = event_constraint_twojet(geometry, independent, spatial['base_rotations'][2],
        spatial['gauge_rotations'][2])
    return histories, raw, psi, geometry, independent, spatial, jets


def _direct_values(geometry, independent, O, R):
    # Independent REAL geometry owner, rather than the analytic Hessian path.
    weights = [intrinsic_m4_weight_jet(12, x[:37], x[37:74], x[74:98],
        source_value=x[98], source_rate=x[99]) for x in geometry]
    lam = [w['mechanical_connection_lambda'].value for w in weights]
    ap = independent[0, 2:]+M*(lam[0]-1)
    ac = independent[1, 2:]+M*(lam[2]-lam[3]+lam[4]-1)
    return np.r_[weights[1]['R4'].value**2-weights[0]['R4'].value**2,
        spatial_connection_row(ap, ac, O, R)]


def test_original_full_connection_constraint_twojet_matches_independent_value_owner(actual):
    _, _, _, geometry, independent, spatial, a = actual
    O, R = spatial['base_rotations'][2], spatial['gauge_rotations'][2]
    np.testing.assert_allclose(a['value'], _direct_values(geometry, independent, O, R),
        atol=4*np.finfo(float).eps)
    assert a['gradient'].shape == (13, CHART_SIZE)
    assert a['hessian'].shape == (13, CHART_SIZE, CHART_SIZE)
    np.testing.assert_allclose(a['hessian'], a['hessian'].swapaxes(1, 2), atol=2e-14, rtol=0)
    # These are actual original field pivots, with no normal-mode selection.
    np.testing.assert_array_equal(a['gradient'][1:, 528:540], np.eye(12))
    assert np.max(abs(a['gradient'][0])) > 1


def test_all_ordered_geometry_field_rotation_second_placements_are_retained(actual):
    _, _, _, geometry, independent, spatial, a = actual
    O, R = spatial['base_rotations'][2], spatial['gauge_rotations'][2]
    rng = np.random.default_rng(113191)
    d = rng.normal(size=CHART_SIZE)*.02
    # The two SO3 exponential placements are varied independently.
    def value(e):
        g = geometry+e*d[:500].reshape(5, 100)
        f = independent+e*d[500:540].reshape(2, 5, 4)
        return _direct_values(g, f, O@expm(e*cross_matrix(d[540:543])),
            expm(e*cross_matrix(d[543:546]))@R)
    h = .001
    first = (value(h)-value(-h))/(2*h)
    second = (value(h)-2*value(0.)+value(-h))/h**2
    np.testing.assert_allclose(first, a['gradient']@d, atol=2e-8, rtol=2e-6)
    np.testing.assert_allclose(second, np.einsum('i,kij,j->k', d, a['hessian'], d),
        atol=5e-8, rtol=2e-5)


def test_multiplier_contact_keeps_both_constraint_curvature_and_normal_frame(actual):
    histories, raw, _, _, _, _, jets = actual
    B = np.zeros((CHART_SIZE, 4), complex)
    for i, (h, r) in enumerate(zip(histories, raw)):
        B[100*i:100*(i+1), 2*i:2*i+2] = proper_normal_coordinate_columns(r,
            h.value(0.)[1], h.original_phase_operands['resolved_phase_coordinate_lift'])['raw_normal_columns'][:100]
    rng = np.random.default_rng(113192)
    xi = rng.normal(size=CHART_SIZE)*.01
    Bx = rng.normal(size=B.shape)*.02
    result = constraint_normal_stationarity_contact(jets, B, Bx, xi)
    np.testing.assert_allclose(result['normal_constraint_multiplier_coefficients'], B.T@jets['gradient'].T)
    np.testing.assert_allclose(result['normal_constraint_multiplier_complete_source'],
        B.T@np.einsum('kij,j->ki', jets['hessian'], xi).T+Bx.T@jets['gradient'].T)
    assert np.linalg.norm(result['normal_constraint_multiplier_source_curvature']) > .01
    assert np.linalg.norm(result['normal_constraint_multiplier_source_frame']) > .01
    # Independent delta-lambda is a second unknown slot, not assigned zero.
    np.testing.assert_array_equal(result['normal_constraint_multiplier_first_variation_coefficient'],
        result['normal_constraint_multiplier_coefficients'])


def test_net_known_action_contact_preserves_rate_slot_and_absent_local_field_argument(actual):
    histories, _, psi, _, _, _, _ = actual
    h = histories[0]
    old, oldt = h.source(0.)
    new, newt = ProvisionalNormalSourceHistory(h, psi[0]).source(0.)
    field = np.zeros(268); field[168] = 1.
    a = known_action_normal_contacts(h, np.array([old, new, field]),
        np.array([oldt, newt, np.zeros(268)]), cap_points=48)
    contacts = a['known_geometry_actual_source_weak_Jacobi_contacts']
    assert np.linalg.norm(contacts[:, 1]-contacts[:, 0]) > 10
    np.testing.assert_array_equal(contacts[:, 2], np.zeros(2))
    assert np.linalg.norm(a['known_geometry_normal_weak_phase_rate_rows']) > 1e-3
    assert abs(a['ambient_lapse']-a['induced_lapse']) > 1e-4
    assert a['known_geometry_raw_Hessian100'].shape == (100, 100)
    assert a['exact_reference_removal_value'] > 1


def test_missing_normal_source_chart_is_rejected(actual):
    jets = actual[-1]
    with pytest.raises(ValueError, match='all four mechanical'):
        constraint_normal_stationarity_contact(jets, np.zeros((CHART_SIZE, 3)),
            np.zeros((CHART_SIZE, 3)), np.zeros(CHART_SIZE))
