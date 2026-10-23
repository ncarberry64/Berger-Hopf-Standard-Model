"""Independent complete-action clock covariance and nonreal first form."""
import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from scripts.evaluate_muon_uniform_clock_action_identity import clock_direction
from bhsm.interface.muon_uniform_clock_action_identity import uniform_clock_action_twojet
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action


def test_uniform_lapse_source_clock_identity_of_full_action_not_zero_energy():
    phase,_=retained_input('outgoing',{})
    raw=phase['arrays'][phase['stage_key']][-1].astype(complex)
    raw[98]+=2e-7j;raw[99]+=3e-7j;raw[263]+=4e-7j
    pairs=phase['arrays']['initial_pair'],phase['arrays']['reference_pair']
    rep=phase['representation'];time=phase['arrays']['stage_coordinate_time'][-1]+2e-8j
    params=dict(nu_squared_action=4,surface_gamma=.11)
    owner=holomorphic_inherited_child_action(raw,time,*pairs,rep,**params)
    a=uniform_clock_action_twojet(raw,time,*pairs,rep,**params)['action']
    np.testing.assert_allclose(a.value,owner['value'],rtol=2e-12,atol=2e-12)
    D=clock_direction(raw,rep)
    np.testing.assert_allclose(owner['raw_gradient']@D+sum(a.gradient),owner['value'],rtol=2e-12,atol=2e-11)
    alpha=1+.001j
    shifted=uniform_clock_action_twojet(raw+(alpha-1)*D,time,*pairs,rep,**params,
        log_uniform_lapse=np.log(alpha),inherited_time_increment=alpha-1)['action']
    np.testing.assert_allclose(shifted.value,alpha*owner['value'],rtol=2e-12,atol=2e-11)
    h=2e-5
    p=uniform_clock_action_twojet(raw,time,*pairs,rep,**params,log_uniform_lapse=h)['action']
    m=uniform_clock_action_twojet(raw,time,*pairs,rep,**params,log_uniform_lapse=-h)['action']
    np.testing.assert_allclose((p.value-m.value)/(2*h),a.gradient[0],rtol=2e-7,atol=2e-8)
    np.testing.assert_allclose((p.gradient-m.gradient)/(2*h),a.hessian[:,0],rtol=3e-7,atol=2e-8)
