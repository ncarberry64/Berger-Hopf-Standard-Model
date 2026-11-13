import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_holomorphic_joint_reference_clock import joint_reference_explicit_clock,reference_affine_raw_rate


def test_joint_explicit_clock_moves_only_reference_and_completes_parent_cotangent():
    phase,_=retained_input('outgoing',{});raw=phase['arrays']['initial_pair'].astype(complex).copy()
    ref=phase['arrays']['reference_pair'].astype(complex).copy();rep=phase['representation']
    raw[0,99]+=.00001j;raw[1,80]+=.00002j;ref[0,38]+=.002;ref[1,61]-=.001
    a=holomorphic_two_arm_action(raw,ref,rep,nu_squared_action=4)
    clock=joint_reference_explicit_clock(raw,ref,rep,a,nu_squared_action=4);rate=reference_affine_raw_rate(ref);h=1e-5
    plus=holomorphic_two_arm_action(raw,ref+h*rate,rep,nu_squared_action=4)
    minus=holomorphic_two_arm_action(raw,ref-h*rate,rep,nu_squared_action=4)
    fd=(plus['gradient']-minus['gradient'])/(2*h)
    np.testing.assert_allclose(clock['gradient_clock_first'],fd,atol=3e-8,rtol=4e-6)
    np.testing.assert_allclose(clock['value_clock_first'],(plus['value']-minus['value'])/(2*h),atol=1e-8,rtol=4e-6)
    assert np.linalg.norm(clock['gradient_clock_first'][:252])>1e-6
    assert clock['actual_parent_partial_clock_count']==0
