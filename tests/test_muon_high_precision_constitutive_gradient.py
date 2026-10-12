import numpy as np
import mpmath as mp
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_high_precision_constitutive_gradient import First,high_precision_original_constitutive_gradient


def test_sparse_arbitrary_precision_dual_retains_independent_complex_source():
    with mp.workdps(65):
        x=First(mp.mpc('0.3','0.2'),{0:mp.mpc(1)});c=mp.mpf('0.12345678901234567890123456789012345')
        a=(x-c)**4/(2+x)
        f=lambda t:(t-c)**4/(2+t)
        exact=mp.diff(f,x.value)
        assert abs(a.gradient[0]-exact)<mp.mpf('1e-60')
        assert abs(a.value-f(x.value))<mp.mpf('1e-60')


def test_original_nonreal_child146_first_gradient_matches_literal_owner():
    phase,_=retained_input('outgoing',{});raw=phase['arrays'][phase['stage_key']][-1].astype(complex)
    raw[99]+=1e-6j;raw[258]+=2e-6j;raw[267]+=3e-7j
    time=phase['arrays']['stage_coordinate_time'][-1]+1e-8j
    args=(phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],phase['representation']);params=phase['receipt']['action_parameters']
    old=holomorphic_inherited_child_action(raw,time,*args,**params)
    new=high_precision_original_constitutive_gradient(raw,time,*args,**params,decimal_precision=50)
    np.testing.assert_allclose(new['constitutive_gradient'],old['gradient'][106:],rtol=2e-10,atol=2e-11)
    np.testing.assert_allclose(new['value'],old['value'],rtol=2e-12,atol=2e-12)
    assert not new['analytic_source_dual_conjugated']
