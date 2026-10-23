import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_complex_endpoint_area_action import original_endpoint_area_coefficient,held_endpoint_hamiltonian_area_coefficients


def test_area_full_original_coefficient_matches_independent_action_parameter():
    phase,_=retained_input('outgoing',{});raw=phase['arrays'][phase['stage_key']][-1].astype(complex)
    raw[99]+=1e-6j;raw[80]+=2e-5j;raw[265]+=1e-6j
    t=phase['arrays']['stage_coordinate_time'][-1]+1e-8j;P=phase['coordinates']['lift']
    args=(phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],phase['representation'])
    base=holomorphic_inherited_child_action(raw,t,*args,nu_squared_action=4,surface_gamma=None)
    changed=holomorphic_inherited_child_action(raw,t,*args,nu_squared_action=4,surface_gamma=.17)
    area=original_endpoint_area_coefficient(raw,P)
    np.testing.assert_allclose(changed['value']-base['value'],.17*area['value'],atol=3e-15)
    np.testing.assert_allclose(changed['gradient']-base['gradient'],.17*area['gradient'],rtol=2e-12,atol=3e-14)
    np.testing.assert_allclose(changed['hessian']-base['hessian'],.17*area['hessian'],rtol=2e-11,atol=4e-13)
    e=np.linalg.solve(P.T@P,P.T@raw);Pi=base['gradient'][106:212]
    energy=held_endpoint_hamiltonian_area_coefficients(e,Pi,base,area)
    fixed=Pi@e[106:212]-changed['value']
    reset=changed['gradient'][106:212]@e[106:212]-changed['value']
    np.testing.assert_allclose(fixed-energy['base'],.17*energy['fixed_target_Pi_area_coefficient'],atol=3e-15)
    np.testing.assert_allclose(reset-energy['base'],.17*energy['same_state_Legendre_Pi_area_coefficient'],atol=3e-15)
    assert np.linalg.norm(area['algebraic_source'])>1e-5
    assert np.max(abs(area['gradient'][144:212]))==0
    assert np.max(abs(area['gradient'][236:]))==0
