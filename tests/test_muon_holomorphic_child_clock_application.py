"""Independent explicit-clock variation of the complete action gradient."""
import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_holomorphic_child_clock_application import holomorphic_child_explicit_clock_application


def test_explicit_clock_contact_matches_full_action_at_fixed_complex_child():
    phase, _ = retained_input('outgoing', {})
    arrays = phase['arrays']
    raw = arrays[phase['stage_key']][-1].astype(complex)
    raw[98] += 1e-8j
    raw[263] += 2e-7j
    time = arrays['stage_coordinate_time'][-1]+1e-8j
    args = (arrays['initial_pair'], arrays['reference_pair'], phase['representation'])
    params = phase['receipt']['action_parameters']
    applied = holomorphic_child_explicit_clock_application(raw, time, *args, **params)
    h = 2e-5
    plus = holomorphic_inherited_child_action(raw, time+h, *args, **params)
    minus = holomorphic_inherited_child_action(raw, time-h, *args, **params)
    np.testing.assert_allclose((plus['value']-minus['value'])/(2*h),
        applied['value_clock_first'], rtol=3e-6, atol=2e-8)
    np.testing.assert_allclose((plus['gradient']-minus['gradient'])/(2*h),
        applied['gradient_clock_first'], rtol=3e-6, atol=4e-8)
    assert applied['analytic_dual_conjugated'] is False
    assert applied['canonical_compatibility_established'] is False
