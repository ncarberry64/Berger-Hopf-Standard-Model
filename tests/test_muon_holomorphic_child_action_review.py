"""Independent literal-owner and complex differential controls for child252."""
import numpy as np

from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_holomorphic_normal_geometry import (
    holomorphic_cap_and_weights, holomorphic_geometry_rows,
)
from bhsm.interface.muon_exact_material_response import (
    exact_moving_cap_action_jet, exact_geometric_connection_coefficient_jets,
)
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet


def _retained():
    phase, _ = retained_input('outgoing', {})
    arrays = phase['arrays']
    return phase, arrays[phase['stage_key']][-1].copy()


def test_holomorphic_cap_and_density_twojets_match_independent_real_owners():
    phase, raw = _retained()
    rep = phase['representation']
    q, v, m = raw[:37], raw[37:74], raw[74:98]
    kwargs = dict(source_value=raw[98], source_rate=raw[99])
    old = exact_moving_cap_action_jet(12, q, v, m, points=rep['cap_points'], **kwargs)
    new = holomorphic_cap_and_weights(raw[:100], points=rep['cap_points'])
    for name in ('total', 'FR_denominator', 'surface_per_gamma'):
        for part in ('value', 'gradient', 'hessian'):
            np.testing.assert_allclose(getattr(new[name], part), getattr(old[name], part),
                                       rtol=2e-12, atol=2e-11)
    weights = intrinsic_m4_weight_jet(12, q, v, m, **kwargs)
    for name in ('wT', 'wS', 'wV', 'R4'):
        for part in ('value', 'gradient', 'hessian'):
            np.testing.assert_allclose(getattr(new[name], part), getattr(weights[name], part),
                                       rtol=2e-12, atol=2e-11)
    selected = rep['rho'][[0, len(rep['rho'])//2, -1]]
    old_geo = exact_geometric_connection_coefficient_jets(12, q, v, m, selected, **kwargs)
    new_geo = holomorphic_geometry_rows(raw[:100], selected)
    for old_row, new_row in zip(old_geo['rows'], new_geo['rows']):
        for name in ('electric', 'radial', 'angular', 'electric_radial', 'shift',
                     'connection_lambda', 'lambda_tau', 'lambda_rho'):
            for part in ('value', 'gradient', 'hessian'):
                np.testing.assert_allclose(getattr(new_row[name], part), getattr(old_row[name], part),
                                           rtol=3e-12, atol=3e-10)


def test_complex_child_action_twojet_is_derivative_of_same_full_action():
    phase, raw = _retained()
    arrays = phase['arrays']
    raw = raw.astype(complex)
    rng = np.random.default_rng(20261011)
    direction = rng.normal(size=len(raw)) + 1j*rng.normal(size=len(raw))
    direction[:100] *= .02
    direction /= np.linalg.norm(direction)
    # Nonreal normal/rate, independent field and scalar coefficients are all
    # reached. A conjugated action or a missing geometry/field block fails.
    raw += 2e-6j * direction
    time = arrays['stage_coordinate_time'][-1] + 1e-8j
    def evaluate(x):
        return holomorphic_inherited_child_action(
            x, time, arrays['initial_pair'], arrays['reference_pair'],
            phase['representation'], **phase['receipt']['action_parameters'])
    base = evaluate(raw)
    h = 2e-5
    plus, minus = evaluate(raw+h*direction), evaluate(raw-h*direction)
    value_first = (plus['value']-minus['value'])/(2*h)
    gradient_first = (plus['raw_gradient']-minus['raw_gradient'])/(2*h)
    np.testing.assert_allclose(value_first, base['raw_gradient']@direction,
                               rtol=3e-8, atol=2e-8)
    np.testing.assert_allclose(gradient_first, base['raw_hessian']@direction,
                               rtol=2e-7, atol=3e-8)
    # The analytic Hessian is symmetric by the action, not a Hilbert dagger.
    np.testing.assert_allclose(base['raw_hessian'], base['raw_hessian'].T,
                               rtol=2e-12, atol=2e-11)
