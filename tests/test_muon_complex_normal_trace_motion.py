import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
from bhsm.interface.muon_complex_paired_normal_action import analytic_normal_frequency_jet,complex_proper_normal_trace
from bhsm.interface.muon_complex_normal_trace_motion import proper_normal_trace_motion,moving_frequency_trial,strong_jacobi_normal_response


def test_actual_nonreal_proper_normal_motion_keeps_lapse_and_wall_mixed_contacts():
    phase,_=retained_input('outgoing',{});x=phase['arrays']['initial_pair'][1].astype(complex).copy();x[98]+=1e-5j
    P=generic_coordinate_lift(phase['representation']['gauge_labels'])['lift']
    rng=np.random.default_rng(22);rate=np.r_[rng.normal(size=100)+.1j*rng.normal(size=100),np.zeros(168)]/100
    a=proper_normal_trace_motion(x,P,rate);h=1e-5
    plus=complex_proper_normal_trace(x+h*rate,P);minus=complex_proper_normal_trace(x-h*rate,P)
    np.testing.assert_allclose(a['trace_coordinate_time_first'],(plus['trace']-minus['trace'])/(2*h),atol=2e-9,rtol=2e-6)
    np.testing.assert_allclose(a['lapse_coordinate_time_first'],(plus['induced_lapse']-minus['induced_lapse'])/(2*h),atol=2e-9,rtol=2e-6)
    assert np.linalg.norm(a['trace_coordinate_time_first'][-1])>1e-3


def test_whole_complex_frequency_trace_clock_motion_vs_literal_reassembly():
    rng=np.random.default_rng(302);n=3;A=rng.normal(size=(8,8))+1j*rng.normal(size=(8,8))*.1
    H=A.T@A+np.eye(8)*4;Hd=np.ones((8,8))*.05+.02j*np.eye(8)
    B=np.array([1,.3j,-.2]);C=np.array([[0,1,.1,0,0]],complex);Bd=np.array([.02j,.01,-.03]);Cd=np.ones_like(C)*.01
    l=.8+.1j;ld=.04-.03j;a=analytic_normal_frequency_jet(H,B,C,lapse=l)
    Td=np.vstack((np.r_[Bd,np.zeros(2)],Cd));d=moving_frequency_trial(a,Hd,Td,ld);h=1e-5
    p=analytic_normal_frequency_jet(H+h*Hd,B+h*Bd,C+h*Cd,lapse=l+h*ld)
    m=analytic_normal_frequency_jet(H-h*Hd,B-h*Bd,C-h*Cd,lapse=l-h*ld)
    np.testing.assert_allclose(d['right_taylor_time_first'],(p['right_taylor']-m['right_taylor'])/(2*h),atol=2e-9,rtol=2e-7)
    np.testing.assert_allclose(d['left_taylor_time_first'],(p['left_taylor']-m['left_taylor'])/(2*h),atol=2e-9,rtol=2e-7)
    np.testing.assert_allclose(d['proper_restoring_time_first'],(p['proper_restoring']-m['proper_restoring'])/(2*h),atol=2e-9,rtol=2e-7)
    assert np.max(abs(d['original_time_first_rows']))<2e-15


def test_nonsymmetric_strong_jacobi_reelimination_is_not_first_insertion():
    p=np.array([[[4+.3j,1],[.2j,3]],[[2j,.4],[-.2j,1j]],[[1,.1],[0,.2]]],complex)
    T=np.array([[1,.3j]],complex);a=strong_jacobi_normal_response(p,T,lapse=.8+.1j)
    omega=1e-4;K=a['bordered_strong_polynomial'];rhs=a['original_rhs']
    direct=-np.linalg.solve(K[0]+omega*K[1]+omega**2*K[2],rhs)[2]
    fitted=a['local_normal_reaction_taylor']@np.array([1,omega,omega**2])
    assert abs(direct-fitted)<2e-11
    assert np.max(abs(a['right_original_rows']))<2e-15
    assert np.max(abs(a['left_original_rows']))<2e-15
    assert np.linalg.norm(a['left_taylor']-a['right_taylor'])>.1
