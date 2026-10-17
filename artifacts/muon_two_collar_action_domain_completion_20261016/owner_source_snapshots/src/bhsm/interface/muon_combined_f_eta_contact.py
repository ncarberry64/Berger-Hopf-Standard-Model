"""Combined action-owned f_eta normal coupling without a unit-normal chart.

v15.26 owns u_eta along grad(f_eta) on the regular wall collar.  In the
foundational D5 term m_eta=-partial_s log sin(f_eta), its normalizing square
root cancels: Eta=-i cot(f)(Gamma0 f0+eps Gamma4 f4). This constructs the
combined local coefficient, not a spacelike unit normal, Gaussian collar
or physical normal-mode normalization. The cohomogeneous f has no angular
derivatives. No source coefficient is conjugated.

Locally D_eta=sin(f) D_min sin(f)^(-1) is a NONUNITARY similarity in
the original geometric current norm. It does not identify their positive
squares/domains or permit deleting eta. Polar sin(f)=0 remains singular.
"""
from __future__ import annotations
import numpy as np

def combined_f_eta_contact(c,*,gamma,carrier_count,angular_count,sheet_orientation):
    G=np.asarray(gamma,complex);nc,nh=int(carrier_count),int(angular_count);eps=int(sheet_orientation)
    if G.shape!=(5,4,4)or nc<1 or nh<1 or eps not in(-1,1):
        raise ValueError("actual full Clifford/carrier/angular and original eta orientation required")
    N,C,z,f,ft,fr=(np.asarray(c[k],complex)for k in(
        "lapse","radial_coframe","coordinate_shift","eta_profile","eta_profile_coordinate_time","eta_profile_radial"))
    if N.ndim!=1 or any(a.shape!=N.shape for a in(C,z,f,ft,fr))or any(not np.isfinite(a).all()for a in(N,C,z,f,ft,fr)):
        raise ValueError("complete same-point coframe and eta profile coefficients required")
    dN,dC,dz,df,dft,dfr=(np.asarray(c[k+"_first"],complex)for k in(
        "lapse","radial_coframe","coordinate_shift","eta_profile","eta_profile_coordinate_time","eta_profile_radial"))
    if dN.ndim!=2 or dN.shape[1:]!=N.shape or not len(dN)or any(a.shape!=dN.shape for a in(dC,dz,df,dft,dfr)):
        raise ValueError("every independent analytic source first must be supplied")
    if any(not np.isfinite(a).all()for a in(dN,dC,dz,df,dft,dfr))or np.any(N==0)or np.any(C==0):
        raise ValueError("finite source firsts and nonzero regular coframe required")
    sine=np.sin(f)
    if np.any(abs(sine)<1e-14):raise ValueError("polar sin(f)=0 requires its owned regular form/trial domain")
    f0=(ft-z*fr)/N;f4=fr/C
    df0=(dft-dz*fr-z*dfr)/N-f0*dN/N;df4=dfr/C-f4*dC/C
    cot=np.cos(f)/sine;dcot=-df/sine**2
    g0,g4=(np.kron(G[j],np.eye(nc*nh))for j in(0,4))
    slash=f0[:,None,None]*g0+eps*f4[:,None,None]*g4
    dslash=df0[:,:,None,None]*g0+eps*df4[:,:,None,None]*g4
    eta=-1j*cot[:,None,None]*slash
    deta=-1j*(dcot[:,:,None,None]*slash[None]+cot[None,:,None,None]*dslash)
    return dict(combined_f_eta_contact=eta,combined_f_eta_contact_first=deta,
        f_timelike_derivative=f0,f_radial_derivative=f4,
        f_gradient_spacelike_square=f4*f4-f0*f0,
        normalizing_square_root_canceled_before_evaluation=True,
        spacelike_unit_normal_or_global_normal_chart_constructed=False,
        sin_f_polar_regular_trial_domain_still_required=True,
        source_coefficients_conjugated=False,physical_mode_normalization_or_exterior_selected=False)
