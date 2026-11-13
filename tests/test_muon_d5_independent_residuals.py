import numpy as np
import pytest
from pathlib import Path
import json
from numpy.polynomial.legendre import leggauss

from bhsm.interface.muon_d5_independent_residuals import (
    SavedOneStepPolynomialField, independent_residual_application, original_strong_rows,
    recovered_export_history,
)


def test_source_has_both_vertex_and_field_placements():
    f = dict(value=np.ones((2, 1))*2, time=np.ones((2, 1))*3,
        radial=np.ones((2, 1))*5, source=np.ones((2, 1))*7,
        time_source=np.ones((2, 1))*11, radial_source=np.ones((2, 1))*13)
    c = {k: np.eye(2)*v for k, v in dict(time=17, radial=19, body=23,
        time_source=29, radial_source=31, body_source=37).items()}
    a = original_strong_rows(f, c)
    assert np.all(a['strong'] == 19*5+17*3+23*2)
    assert np.all(a['source_vertex'] == 31*5+29*3+37*2)
    assert np.all(a['source_field'] == 19*13+17*11+23*7)
    assert np.all(a['strong_source'] == a['source_vertex']+a['source_field'])


def test_block_operator_preserves_all_carriers_and_comparison_difference():
    f = {k: np.arange(12).reshape(4, 3)+i for i, k in enumerate(
        ('value', 'time', 'radial', 'source', 'time_source', 'radial_source'))}
    c = {k: np.array([np.eye(2)*(j+1), np.eye(2)*(j+2)]) for j, k in enumerate(
        ('time', 'radial', 'body', 'time_source', 'radial_source', 'body_source'))}
    comparison = {k: a.copy() for k, a in c.items()}
    comparison['body'] -= np.eye(2)
    arrays, report = independent_residual_application(lambda t, r: f, lambda t, r: c,
        [[.2, .7], [.8, .4]], comparison_coefficient_evaluate=lambda t, r: comparison,
        carrier_block_size=2)
    np.testing.assert_allclose(arrays['coefficient_difference_strong'][0], f['value'])
    np.testing.assert_allclose(arrays['coefficient_difference_strong_source'][0], f['source'])
    assert len(report['carrier_blocks']) == 2
    assert report['field_input_columns'] == 3
    assert report['bulk_term_scaled_relative'] > 0


def test_saved_polynomial_derivatives_are_not_equation_replacements():
    t = np.array([0., .1, .31, .64, .91, 1.])*1e-5
    exact_radial_coordinates = np.r_[0., (leggauss(3)[0]+1)/2, 1.]
    radial = 1.57-exact_radial_coordinates*1e-7
    shared = dict(times=t, radial_nodes=radial, radial_node_step=np.zeros(5))
    z = t[None, :]/1e-5
    x = exact_radial_coordinates[:, None]
    dr = radial[-1]-radial[0]
    # Exact cubic in r and fifth degree in t; complex first source independent.
    v = 2+x**3+z**5+x*z
    vx = 1j*(3*x**2+z**4)
    data = dict(value=v, time=(5*z**4+x)/1e-5,
        radial=(3*x**2+z)/dr, source=vx,
        time_source=1j*(4*z**3+np.zeros_like(x))/1e-5,
        radial_source=1j*(6*x+np.zeros_like(z))/dr)
    data = {'p_'+k: np.broadcast_to(a, (5, 6))[:, :, None, None] for k, a in data.items()}
    adapter = SavedOneStepPolynomialField(shared, data, 'p')
    got = adapter(.413e-5, 1.57-.319e-7)
    x1 = ((1.57-.319e-7)-radial[0])/dr
    assert abs(got['value'][0, 0]-(2+x1**3+.413**5+x1*.413)) < 1e-13
    assert abs(got['time'][0, 0]-(5*.413**4+x1)/1e-5) < 1e-7
    assert abs(got['radial'][0, 0]-(3*x1**2+.413)/dr) < 1e-6
    checks = adapter.saved_derivative_checks()
    # Physical rho is stored in binary64: its rounding is amplified by the
    # deliberately 1e-7-wide chart and must not be confused with a PDE error.
    assert checks['value'] < 1e-7
    assert checks['source'] < 1e-7
    with pytest.raises(ValueError, match='outside'):
        adapter(-1e-6, radial[2])


def test_missing_source_and_mismatched_carriers_are_rejected():
    with pytest.raises(ValueError, match='complete'):
        original_strong_rows({}, {})
    f = {k: np.ones((4, 2)) for k in
        ('value', 'time', 'radial', 'source', 'time_source', 'radial_source')}
    c = {k: np.eye(3) for k in
        ('time', 'radial', 'body', 'time_source', 'radial_source', 'body_source')}
    with pytest.raises(ValueError, match='identities'):
        original_strong_rows(f, c)


@pytest.mark.parametrize('side', ['incoming', 'outgoing'])
def test_recovered_original_callback_matches_every_current_sample(side):
    root = Path(__file__).resolve().parents[1]
    folder = root/'artifacts/muon_retained_response_20261018/inputs'
    md = json.loads((folder/'history_metadata.json').read_bytes())
    with np.load(folder/(side+'_history.npz'), allow_pickle=False) as z:
        samples = md['sides'][side]
        t = np.array([s['time'] for s in samples])
        raw = np.array([z[s['label']+'_raw_fields'] for s in samples])
        rates = np.array([z[s['label']+'_raw_coordinate_time_derivative'] for s in samples])
    history, receipt = recovered_export_history(root, side, t, raw, rates)
    assert receipt['all_six_raw268_bitwise_match']
    assert receipt['all_six_rate268_bitwise_match']
    for i, ti in enumerate(t):
        x, xt = history.value(ti)
        assert np.array_equal(x, raw[i])
        assert np.array_equal(xt, rates[i])
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    wall = history.gauge_basis(np.array([WALL]))
    np.testing.assert_array_equal(wall[0, :, :60], np.zeros((20, 60)))
    np.testing.assert_array_equal(wall[0, :, 60:], np.eye(20))
    with pytest.raises(ValueError, match='extrapolated'):
        history.value(t[-1]+1e-5)
