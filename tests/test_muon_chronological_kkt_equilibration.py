import numpy as np
from bhsm.interface.muon_chronological_kkt_equilibration import equilibrate_chronological_kkt,original_chronological_kkt_apply
from bhsm.interface.muon_chronological_spectral_blocks import chronological_spectral_factor,chronological_source_solve


def test_indefinite_complex_constraint_and_primal_rows_survive_equilibration():
    rng=np.random.default_rng(861);n=5;d=7
    D=[]
    for _ in range(n):
        H=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5));H=H+H.T+7*np.eye(5)
        C=rng.normal(size=(2,5))+.1j*rng.normal(size=(2,5))
        D.append(np.block([[H,C.T],[C,np.zeros((2,2))]]))
    D=np.array(D);U=.02*(rng.normal(size=(n-1,d,d))+1j*rng.normal(size=(n-1,d,d)));L=U.transpose(0,2,1).copy()
    units=np.tile(np.array([1e6,1e3,1e-2,1e4,1.,1e-4,1e-6]),(n,1))
    D*=units[:,:,None]*units[:,None,:];U*=units[:-1,:,None]*units[1:,None,:];L*=units[1:,:,None]*units[:-1,None,:]
    x=(rng.normal(size=(n,d))+1j*rng.normal(size=(n,d)))/units
    rhs=original_chronological_kkt_apply(D,U,L,x)
    eq=equilibrate_chronological_kkt(D,U,L,iterations=10);s=eq['coordinate_scales']
    f=chronological_spectral_factor(eq['diagonal'],eq['upper'],eq['lower'])
    y=np.array(chronological_source_solve(f,list(s*rhs)));got=s*y
    np.testing.assert_allclose(got*units,x*units,rtol=2e-12,atol=2e-12)
    residual=original_chronological_kkt_apply(D,U,L,got)-rhs
    np.testing.assert_allclose(residual/units,0,atol=5e-12)
    np.testing.assert_allclose(eq['diagonal'],s[:,:,None]*D*s[:,None,:],rtol=3e-14,atol=3e-14)
    assert np.all(eq['diagonal'][:,5:,5:]==0)
