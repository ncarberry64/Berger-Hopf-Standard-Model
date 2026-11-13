"""Associated-section phase obstruction and full temporal connection jet."""
import numpy as np
import pytest
from scipy.linalg import expm

from bhsm.interface.muon_d5_higgs_temporal_bundle_application import (
    complex_higgs,real_higgs,necessary_higgs_phase,temporal_bundle_jet,
)


def test_necessary_phase_solves_actual_parallel_sections_without_log_branch():
    p=np.array([.2+.1j,1.1-.3j]);K=expm(np.array([[.1j,.2],[-.2,-.1j]]))
    factor=np.exp(1.7j);c=factor*K@p
    phase,row=necessary_higgs_phase(p,c,K)
    assert abs(phase-factor)<3e-16
    np.testing.assert_allclose(row,0,atol=3e-16)
    np.testing.assert_array_equal(complex_higgs(real_higgs(p)),p)


def test_phase_does_not_erase_perpendicular_or_norm_mismatch():
    p=np.array([0.,1.]);K=np.eye(2);c=np.array([.03,1.1j])
    phase,row=necessary_higgs_phase(p,c,K)
    assert abs(phase-1j)<1e-16
    assert np.max(abs(row))>.09
    assert abs(np.vdot(phase*K@p,row).imag)<1e-16
    with pytest.raises(ValueError,match='nonzero'):
        necessary_higgs_phase(p,np.array([1.,0.]),K)


def test_temporal_bundle_jacobi_includes_both_vertices_clock_and_unknown_map():
    rng=np.random.default_rng(611)
    z=rng.normal(size=(5,2,2))+1j*rng.normal(size=(5,2,2))
    Ap,Ac,Apx,Acx,T=z-z.conj().swapaxes(-1,-2)
    U=expm(T*.13);Ux=T@U;k,kx=.63,-1.7
    app=temporal_bundle_jet(Ap,Ac,U,k,Ap_first=Apx,Ac_first=Acx,
        kappa_first=kx,U_first=Ux)
    assert np.max(abs(app['original_row']))<1e-15
    assert np.max(abs(app['original_first_row']))<2e-15
    def direct(e):
        u=expm(e*T)@U
        return -(Ac+e*Acx)@u+(k+e*kx)*u@(Ap+e*Apx)
    h=1e-6
    np.testing.assert_allclose((direct(h)-direct(-h))/(2*h),app['time_first'],atol=5e-10)
    incomplete=-Acx@U+k*U@Apx
    assert np.linalg.norm(app['time_first']-incomplete)>1
