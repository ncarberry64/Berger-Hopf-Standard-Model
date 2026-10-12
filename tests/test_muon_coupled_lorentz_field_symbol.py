import numpy as np
from bhsm.interface.muon_coupled_lorentz_field_symbol import apply_weak_symbol
from bhsm.interface.muon_local_normal_action_symbol import chronological_frequency_polynomial


def test_proper_frequency_density_matches_original_full_x_v_y_action():
    rng=np.random.default_rng(31);n=7;m=3;raw=rng.normal(size=(2*n+m,2*n+m));H=raw+raw.T
    omega=.71;lapse=.83;p=chronological_frequency_polynomial(H,n)
    coeff=np.array([p['constant']/lapse,1j*p['imaginary_linear'],lapse*p['quadratic']])
    right=rng.normal(size=(n+m,4))+1j*rng.normal(size=(n+m,4))
    L=np.zeros((2*n+m,n+m),complex);L[:n,:n]=np.eye(n);L[n:2*n,:n]=1j*omega*lapse*np.eye(n);L[2*n:,n:]=np.eye(m)
    direct=L.conj().T@H@L/lapse@right
    assert np.allclose(apply_weak_symbol(coeff,omega,right),direct,rtol=1e-14,atol=1e-14)
