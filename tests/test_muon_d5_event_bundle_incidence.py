"""Independent geometry, curvature and nonidentity event-incidence checks."""
from pathlib import Path
import json
import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_d5_event_bundle_incidence import (
    original_event_coefficients, wall_event_incidence, radial_cauchy_geometry,
    radial_cauchy_incidence_point, right_frame_curvature, curvature_invariants,
    temporal_transition_generator,
)
from bhsm.interface.muon_d5_independent_residuals import recovered_export_history
from bhsm.interface.muon_sigma_normal_collar_transport import sigma_geometry_point
from bhsm.interface.muon_parent_retarded_hypercharge import WALL

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def histories():
    folder = ROOT/'artifacts/muon_retained_response_20261018/inputs'
    metadata = json.loads((folder/'history_metadata.json').read_bytes())
    out = {}
    for side in ('incoming', 'outgoing'):
        samples = metadata['sides'][side]
        with np.load(folder/(side+'_history.npz'), allow_pickle=False) as z:
            t = np.array([s['time'] for s in samples])
            x = np.array([z[s['label']+'_raw_fields'] for s in samples])
            dx = np.array([z[s['label']+'_raw_coordinate_time_derivative'] for s in samples])
        out[side] = recovered_export_history(ROOT, side, t, x, dx)[0]
    return out


def test_original_radial_two_jet_against_original_geometry_callback(histories):
    raw, first = histories['incoming'].value(0.)
    rho = WALL-.03
    a = radial_cauchy_geometry(raw, first, rho)
    b = sigma_geometry_point(raw, first, rho)
    assert abs(a['radius']-b['radius'][0]) < 2e-15
    assert abs(a['radial_coframe']-b['radial_coframe'][0]) < 2e-15
    assert abs(a['radius_radial']-b['radius'][0]*b['radius_log_radial'][0]) < 2e-14
    h = 2e-5
    values = [sigma_geometry_point(raw, first, rho+k*h)['radius'][0] for k in (-2, -1, 0, 1, 2)]
    independent_first = (values[0]-8*values[1]+8*values[3]-values[4])/(12*h)
    independent_second = (-values[0]+16*values[1]-30*values[2]+16*values[3]-values[4])/(12*h*h)
    assert abs(a['radius_radial']-independent_first) < 3e-11
    assert abs(a['radius_radial_second']-independent_second) < 3e-6


def test_radius_incidence_consumes_actual_geometry_and_retains_other_metric_nonpass(histories):
    p, px = histories['incoming'].value(0.)
    c, cx = histories['outgoing'].value(0.)
    width = 1.1875863735508981e-7
    arrays, report = radial_cauchy_incidence_point(p, px, c, cx, WALL-.47*width,
        parent_bounds=(WALL-width, WALL), child_rho_first=0.)
    assert report['root_in_saved_parent_domain']
    assert abs(arrays['parent_rho']-arrays['child_rho']) > 2e-8
    assert abs(arrays['radius_row']) < 5e-16
    assert abs(arrays['radius_first_row']) < 1e-14
    assert 1.51 < arrays['radial_tangent'].real < 1.52
    assert abs(arrays['radial_metric_row']) > .48
    assert not report['full_event_map_selected']
    assert not report['physical_admission']
    failed, no_root = radial_cauchy_incidence_point(p, px, c, cx, WALL-.89*width,
        parent_bounds=(WALL-width, WALL), child_rho_first=0.)
    assert not no_root['root_in_saved_parent_domain']
    assert 'parent_rho' not in failed


def test_curvature_uses_noncoordinate_right_frame_and_analytic_source():
    rng = np.random.default_rng(152)
    z = rng.normal(size=(6, 2, 2))+1j*rng.normal(size=(6, 2, 2))
    z = z-z.conj().swapaxes(-1, -2)
    A, Ax = z[:3], z[3:]
    F, Fx = right_frame_curvature(A, Ax)
    np.testing.assert_allclose(F[0], 2*A[0]+A[1]@A[2]-A[2]@A[1], atol=1e-14)
    h = 1e-5
    plus = right_frame_curvature(A+h*Ax, Ax)[0]
    minus = right_frame_curvature(A-h*Ax, Ax)[0]
    np.testing.assert_allclose(Fx, (plus-minus)/(2*h), atol=5e-10)


def test_curvature_invariants_do_not_choose_angular_or_gauge_map():
    rng = np.random.default_rng(153)
    z = rng.normal(size=(6, 2, 2))+1j*rng.normal(size=(6, 2, 2))
    z = z-z.conj().swapaxes(-1, -2)
    F, Fx = z[:3], z[3:]
    U = expm(np.array([[.2j, .1+.3j], [-.1+.3j, -.1j]]))
    O = expm(np.array([[0., -.3, .2], [.3, 0., -.1], [-.2, .1, 0.]]))
    transformed = np.einsum('ij,jab->iab', O, U@F@U.conj().T)
    transformed_first = np.einsum('ij,jab->iab', O, U@Fx@U.conj().T)
    a, b = curvature_invariants(F, Fx), curvature_invariants(transformed, transformed_first)
    np.testing.assert_allclose(a['invariants'], b['invariants'], rtol=2e-13, atol=2e-11)
    np.testing.assert_allclose(a['invariants_first'], b['invariants_first'], rtol=2e-13, atol=2e-10)
    h = 1e-6
    fd = (curvature_invariants(F+h*Fx, Fx)['invariants']
        -curvature_invariants(F-h*Fx, Fx)['invariants'])/(2*h)
    np.testing.assert_allclose(a['invariants_first'], fd, rtol=2e-8, atol=2e-7)


def test_temporal_connection_equation_solved_for_all_initial_bundle_columns():
    Ap = np.array([[.2j, .3], [-.3, -.1j]])
    Ac = np.array([[.3j, -.2j], [-.2j, .1j]])
    Apx, Acx = Ap/3, Ac/5
    k, kx = .63, -.07
    L, Lx = temporal_transition_generator(Ap, Ac, k,
        parent_first=Apx, child_first=Acx, clock_first=kx)
    for U in np.eye(4).reshape(4, 2, 2):
        dU = (L@U.ravel()).reshape(2, 2)
        np.testing.assert_allclose(dU+Ac@U-k*U@Ap, 0, atol=1e-16)
        dUx = (Lx@U.ravel()).reshape(2, 2)
        np.testing.assert_allclose(dUx+Acx@U-kx*U@Ap-k*U@Apx, 0, atol=1e-16)


def test_actual_wall_clock_and_frame_are_nonidentity_and_Xi_nonpass_stays(histories):
    p = original_event_coefficients(histories['incoming'], 0., [WALL], side='parent')
    c = original_event_coefficients(histories['outgoing'], 0., [WALL], side='child')
    arrays, report = wall_event_incidence(p, c)
    assert .62 < report['clock_differential_child_to_parent'] < .64
    assert report['clock_residual'] < 1e-15
    assert report['relative_boost_departure_from_identity'] > .02
    assert report['spatial_metric_max'] < 1e-14
    assert report['spatial_metric_Xi_max'] > .1
    assert report['curvature']['SM16']['curvature_invariant_Xi_max'] > .7
    assert not report['angular_SO3_tangent_selected']
    assert not report['physical_bundle_initial_map_selected']
    assert np.max(abs(arrays['parent_current_frame_rows'])) < 1e-14
    assert np.max(abs(arrays['child_current_frame_rows'])) < 1e-14
    with pytest.raises(ValueError, match='every raw'):
        original_event_coefficients(histories['outgoing'], 0., [WALL], side='child',
            directions={'raw': np.zeros((268, 1))})
