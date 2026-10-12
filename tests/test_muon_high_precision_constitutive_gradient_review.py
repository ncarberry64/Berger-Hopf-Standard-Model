"""Independent full original146 owner control of the arbitrary precision AD."""
import numpy as np
from scripts.evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_high_precision_constitutive_gradient import high_precision_original_constitutive_gradient


def test_arbitrary_precision_full_original146_nonreal_gradient_matches_owner():
    phase,_=retained_input('outgoing',{})
    raw=phase['arrays'][phase['stage_key']][-1].astype(complex)
    # Reach every original velocity/multiplier/At row on an independent
    # nonreal tangent, at modest rates where the ordinary owner is resolved.
    rng=np.random.default_rng(14620261012)
    P=phase['coordinates']['lift']
    d=np.r_[np.zeros(106),rng.normal(size=146)]
    raw+=1e-6j*(P@d)
    time=phase['arrays']['stage_coordinate_time'][-1]+2e-8j
    pairs=phase['arrays']['initial_pair'],phase['arrays']['reference_pair']
    params=dict(nu_squared_action=4,surface_gamma=.11)
    old=holomorphic_inherited_child_action(raw,time,*pairs,phase['representation'],**params)
    new=high_precision_original_constitutive_gradient(raw,time,*pairs,phase['representation'],
        **params,decimal_precision=50)
    np.testing.assert_allclose(new['value'],old['value'],rtol=3e-12,atol=2e-11)
    np.testing.assert_allclose(new['constitutive_gradient'],old['gradient'][106:],rtol=3e-11,atol=3e-10)
    assert len(new['gradient_decimal_strings'])==146
