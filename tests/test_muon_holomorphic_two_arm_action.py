import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_two_arm_action import holomorphic_two_arm_action
from bhsm.interface.muon_birth_finite_normal_trace_graph import finite_normal_trace_graph_action_two_jet


def _input():
    phase,_=retained_input('outgoing',{});raw=phase['arrays']['initial_pair'].copy()
    raw[0,98]+=1e-5;raw[1,98]-=1e-5;raw[1,102]+=2e-5
    return phase,raw,phase['arrays']['reference_pair']


def test_real_full536_graph_matches_retained_independent_owner():
    phase,raw,ref=_input();rep=phase['representation']
    old=finite_normal_trace_graph_action_two_jet(raw,ref,rep,nu_squared_action=4,surface_gamma=.07)
    new=holomorphic_two_arm_action(raw,ref,rep,nu_squared_action=4,surface_gamma=.07)
    np.testing.assert_allclose(new['value'],old['value'],rtol=3e-12,atol=3e-13)
    np.testing.assert_allclose(new['raw_gradient'],old['raw_gradient'],rtol=2e-10,atol=5e-12)
    np.testing.assert_allclose(new['raw_hessian'],old['raw_hessian'],rtol=2e-10,atol=5e-11)
    assert np.linalg.norm(new['source_Hessian_contact'][:100,268:])>1e-5


def test_nonreal_all536_direction_and_temporal_orientation():
    phase,raw,ref=_input();raw=raw.astype(complex);raw[0,99]+=1e-6j;raw[1,80]+=2e-6j;raw[1,267]+=3e-7j
    rep=phase['representation'];a=holomorphic_two_arm_action(raw,ref,rep,nu_squared_action=4)
    j=np.arange(536);d=(np.sin(.71*(j+1))+.3j*np.cos(.43*(j+1)))/np.sqrt(536);h=2e-6
    p=holomorphic_two_arm_action(raw+h*d.reshape(2,268),ref,rep,nu_squared_action=4)
    m=holomorphic_two_arm_action(raw-h*d.reshape(2,268),ref,rep,nu_squared_action=4)
    np.testing.assert_allclose(a['raw_gradient']@d,(p['value']-m['value'])/(2*h),rtol=3e-7,atol=3e-8)
    np.testing.assert_allclose(a['raw_hessian']@d,(p['raw_gradient']-m['raw_gradient'])/(2*h),rtol=3e-7,atol=3e-7)
    np.testing.assert_allclose(a['raw_hessian'],a['raw_hessian'].T,rtol=2e-13,atol=2e-12)
    theta=-a['gradient'][a['velocity_indices']].copy();theta[:106]+=2*a['parent']['gradient'][106:212]
    np.testing.assert_array_equal(a['temporal_cotangent'],theta)
    assert np.linalg.norm(a['raw_gradient'].imag)>1e-5
