import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_high_precision_canonical_compatibility import high_precision_original_constitutive_action
from bhsm.interface.muon_complex_canonical_midpoint import complex_canonical_midpoint_rows


def test_actual_precise_tail_canonical_Jacobian_retains_original_complex_rows():
    phase,_=retained_input('outgoing',{});P=phase['coordinates']['lift']
    raw=phase['arrays'][phase['stage_key']][-1].astype(complex)
    raw[99]+=1e-6j;raw[258]+=2e-6j;raw[267]+=3e-7j
    eta=np.linalg.solve(P.T@P,P.T@raw);t=phase['arrays']['stage_coordinate_time'][-1]+1e-8j
    args=(phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],phase['representation'])
    params=phase['receipt']['action_parameters']
    evaluate=lambda e:high_precision_original_constitutive_action(P@e,t,*args,decimal_precision=50,**params)
    base=evaluate(eta);n=106;h=1e-8-2e-9j;Pi=base['gradient'][n:2*n];x=eta[:n]
    z=np.r_[x+h*eta[n:2*n],Pi+h*base['gradient'][:n],eta[n:]]
    a=complex_canonical_midpoint_rows(z,x,Pi,h,evaluate)
    j=np.arange(146);direction=np.r_[np.zeros(212,complex),(.5*np.sin(j+.4)+.3j*np.cos(.6*j))/np.sqrt(146)]
    eps=2e-5
    plus=complex_canonical_midpoint_rows(z+eps*direction,x,Pi,h,evaluate)['residual']
    minus=complex_canonical_midpoint_rows(z-eps*direction,x,Pi,h,evaluate)['residual']
    np.testing.assert_allclose(a['jacobian']@direction,(plus-minus)/(2*eps),rtol=3e-7,atol=3e-8)
    # Original position force is preserved as a separate action application,
    # with no fixed-x material cotangent substituted into the canonical row.
    np.testing.assert_array_equal(base['gradient'][:n],base['binary_original_gradient'][:n])
    assert len(a['residual'])==358 and len(base['high_precision_gradient_decimal_strings'])==146
