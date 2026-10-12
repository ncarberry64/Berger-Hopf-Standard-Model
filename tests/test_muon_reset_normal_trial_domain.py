import numpy as np
from bhsm.interface.muon_reset_normal_trial_domain import frequency_master_trial_lifts
from bhsm.interface.muon_complex_paired_normal_action import analytic_frequency_polynomial


def test_frequency_state_restore_keeps_original_velocity_sign_and_analytic_action():
    rng=np.random.default_rng(612)
    order=np.r_[np.arange(106),252+np.arange(106),106+np.arange(106),358+np.arange(106),
                212+np.arange(40),464+np.arange(40)]
    left=rng.normal(size=(292,3))+1j*rng.normal(size=(292,3))
    right=rng.normal(size=(292,3))+1j*rng.normal(size=(292,3))
    L=frequency_master_trial_lifts(left,order,left=True)
    R=frequency_master_trial_lifts(right,order)
    H=rng.normal(size=(504,504))+1j*rng.normal(size=(504,504))
    p=analytic_frequency_polynomial(H[np.ix_(order,order)],212)
    literal=np.array([sum(L[:,i]@H@R[:,k-i]for i in range(k+1))for k in range(3)])
    reduced=np.array([sum(left[:,i]@p[j]@right[:,k-i-j]
        for i in range(k+1)for j in range(k-i+1))for k in range(3)])
    np.testing.assert_allclose(literal,reduced,rtol=3e-14,atol=1e-10)
    np.testing.assert_array_equal(R[106:212,0],0)
    np.testing.assert_allclose(R[358:464,1:],1j*R[252:358,:2],atol=0)
    np.testing.assert_allclose(L[106:212,1:],-1j*L[:106,:2],atol=0)
