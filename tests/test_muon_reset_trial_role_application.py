import numpy as np
from bhsm.interface.muon_reset_trial_role_application import (
    RESET_ROLES, reset_role_indices, reset_trial_role_application,
    canonical_variational_constitutive_rows)


def test_roles_preserve_natural_force_and_canonical_source():
    lengths = dict(gauge_trace=64,Higgs_trace=4,moving_geometric_trace=4,
        normal_position_trace=1,incoming_constraints=40,child_constraints=40,
        incoming_energy=1,child_energy=1,gauge_temporal_dual=64,
        Higgs_temporal_dual=4,common_attachment_temporal_dual=2,
        common_normal_temporal_dual=1)
    groups={}; start=0
    for names in RESET_ROLES.values():
        for name in names:
            groups[name]=list(range(start,start+lengths[name]));start+=lengths[name]
    roles=reset_role_indices(groups)
    assert [len(roles[k])for k in RESET_ROLES]==[73,80,73]
    rng=np.random.default_rng(437); H=rng.normal(size=(504,504))+1j*rng.normal(size=(504,504))
    z=rng.normal(size=504)+1j*rng.normal(size=504);g=rng.normal(size=504)+1j*rng.normal(size=504)
    x=np.r_[np.arange(106),np.arange(252,358)];v=x+106;y=np.r_[np.arange(212,252),np.arange(464,504)]
    p=H[v]@z+g[v]
    a=canonical_variational_constitutive_rows(H,z,p,g)
    phase=np.r_[v,y]
    np.testing.assert_allclose(a['phase_Hessian']@z[phase]-a['phase_rhs'],
        a['original292_constitutive_rows'],rtol=2e-14,atol=2e-12)
    np.testing.assert_allclose(a['original212_momentum_rate'],H[x]@z+g[x])
    J=rng.normal(size=(226,504));s=rng.normal(size=(226,1));b=reset_trial_role_application(J,z[:,None],groups,source_rows=s)
    np.testing.assert_allclose(b['original226_total_rows'],J@z[:,None]+s)
    assert b['roles']['natural_response']['max_abs_by_coefficient'][0]>0
    assert b['natural_response_is_not_forced_zero']
