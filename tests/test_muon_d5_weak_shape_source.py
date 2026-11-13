"""Independent dense trial action check of all density/source placements."""
import numpy as np
from bhsm.interface.muon_d5_weak_shape_source import fixed_radial_d5_weak_source


def test_density_and_radial_coefficient_products_match_whole_trial_difference():
    rng=np.random.default_rng(330);q,d,n=5,4,3
    D,R,dD,dR=[rng.normal(size=(q,d,d))+1j*rng.normal(size=(q,d,d))for _ in range(4)]
    mu=rng.normal(size=q)+1j*rng.normal(size=q);dm=rng.normal(size=q)+1j*rng.normal(size=q);w=rng.random(q)
    B,Br=rng.normal(size=(q,n)),rng.normal(size=(q,n));G=rng.normal(size=(d,d))+.1j*rng.normal(size=(d,d))
    z=fixed_radial_d5_weak_source(dict(original_D5_zero_order=D,direct_source_D5_zero_order=dD,
        original_D5_radial_principal=R,direct_source_D5_radial_principal=dR),mu,dm,w,B,Br,time_Clifford=G)
    def independent(h):
        value=np.zeros((n*d,n*d),complex)
        for i in range(q):
            V=np.concatenate([B[i,j]*np.eye(d)for j in range(n)],axis=1)
            Vr=np.concatenate([Br[i,j]*np.eye(d)for j in range(n)],axis=1)
            L=V.T@G
            value+=w[i]*(mu[i]+h*dm[i])*L@((D[i]+h*dD[i])@V+(R[i]+h*dR[i])@Vr)
        return value
    assert np.max(abs(independent(0)-z['original_fixed_radial_weak_action']))<2e-14
    h=1e-5;fd=(independent(h)-independent(-h))/(2*h)
    assert np.max(abs(fd-z['direct_shape_fixed_radial_weak_action']))<2e-9
