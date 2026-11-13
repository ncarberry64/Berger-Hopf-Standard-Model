"""Focused checks of new quotient density and source duality, not anomaly."""
from pathlib import Path
import numpy as np
import pytest
try:
    from muon_parent_maxwell_velocity import (current_parent_fields,
        local_velocity_density,electromagnetic_trace_coefficient,
        temporal_and_radial_flux,MissingConnectionAttachment)
except ModuleNotFoundError:
    from bhsm.interface.muon_parent_maxwell_velocity import (current_parent_fields,
        local_velocity_density,electromagnetic_trace_coefficient,
        temporal_and_radial_flux,MissingConnectionAttachment)

HERE=Path(__file__).resolve().parent
DATA=HERE/'inputs.npz'
if not DATA.exists():
    DATA=HERE.parent/'artifacts/muon_parent_geometry_20261001/inputs.npz'

def test_current_quotient_identity_and_clock_pullback():
    data=np.load(DATA,allow_pickle=False)
    f=current_parent_fields(data['states'],data['log_R4'],np.array([np.pi/2]))
    q=data['states'][:,:37]
    vb=q[:,25:37]@((-1.)**np.arange(12))
    assert np.allclose(f['base_radius'][:,0],np.exp(data['log_R4']),rtol=3e-15)
    assert np.allclose(f['fiber_radius'][:,0],2*np.exp(data['log_R4'])*np.cosh(2*vb),rtol=3e-15)
    assert np.allclose(f['proper_lapse'][:,0],1,rtol=0,atol=1e-15)
    assert np.allclose(f['raw_lapse'][:,0],np.exp(data['log_boundary_lapse']),rtol=3e-15)

def test_velocity_density_from_metric_inverse_with_radial_shift():
    # Independent ADM determinant/inverse computation; a nonzero radial
    # shift changes mixed tau/rho derivatives, but not the velocity block.
    data=np.load(DATA,allow_pickle=False)
    f=current_parent_fields(data['states'][:1],data['log_R4'][:1],np.array([np.pi/4]))
    d=local_velocity_density(f,angular_haar_Gram=data['angular_Haar_Gram'])
    C,r,nu,zeta=[float(f[k][0,0]) for k in
                  ('C_rho','base_radius','proper_lapse','proper_shift_rho')]
    g=np.diag([nu*nu,C*C,r*r,r*r,r*r])
    g[0,0]+=C*C*zeta*zeta; g[0,1]=g[1,0]=C*C*zeta
    gi=np.linalg.solve(g,np.eye(5))
    density=np.sqrt(np.linalg.det(g))*float(f['connection_component_coefficient_per_kappa1'][0,0])*float(f['Lambda'][0])*(gi[0,0]*gi[2,2]-gi[0,2]*gi[0,2])
    assert 2*np.pi**2*density==pytest.approx(d['beta_velocity_density_per_kappa1_cQ'][0,0],rel=3e-14)
    T=1/np.sqrt(2*np.pi**2*float(f['boundary_radius'][0]))
    assert T*T*d['beta_velocity_density_per_kappa1_cQ'][0,0]==pytest.approx(d['b_velocity_density_per_kappa1_cQ'][0,0],rel=3e-15)

def test_flux_from_one_bilinear_and_unselected_attachment():
    b,bt,br,e,r,zeta,H=.3,.7,-.2,1.7,.8,.6,-.4
    pi_t,pi_r=temporal_and_radial_flux(b,bt,br,e=e,r=r,shift=zeta,H=H,radial_form_sign=-1)
    def L(t,s):
        return .5*(e*(t-zeta*s-H*b/2)**2-r*s*s)
    h=1e-5
    assert pi_t==pytest.approx((L(bt+h,br)-L(bt-h,br))/(2*h),abs=2e-11)
    assert pi_r==pytest.approx((L(bt,br+h)-L(bt,br-h))/(2*h),abs=2e-11)
    with pytest.raises(MissingConnectionAttachment):
        electromagnetic_trace_coefficient(1.)
