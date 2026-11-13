"""Real positive-coframe conversion of the full action-owned f covector.

The premise is explicit: use the existing real positive-coframe geometric
branch and carry the SAME connection one-form -d log sin(f). This derives
its native first-order coefficient; it does not identify the whole AE4
graded carrier, a global input/adjoint/outgoing domain, or a physical E map.
No analytic time-coordinate contour is selected here.

The local identity A_cov=sin(f) A_min sin(f)^-1 is nonunitary in geometric
L2. It never permits removing eta, changing its Riesz density or crossing
the polar sin(f)=0 endpoint without the separately proved form domain.
"""
from __future__ import annotations
import numpy as np


def _value_and_first(c,name,shape=None):
    v=np.asarray(c[name],complex);d=np.asarray(c[name+'_first'],complex)
    if v.ndim!=1 or (shape is not None and v.shape!=shape)or d.ndim!=2 or d.shape[1:]!=v.shape or not d.shape[0]:raise ValueError(name+': complete scalar value/source-first axes required')
    if not np.isfinite(v).all()or not np.isfinite(d).all():raise ValueError(name+': finite coefficients required')
    return v,d


def real_positive_d5_covector_binding(c,*,gamma,sheet_orientation):
    """Return full Spin4 coefficients and analytic firsts, without truncation.

    Supplied first axes are analytic source directions and are never
    conjugated. Tensoring the returned Spin4 coefficient with the OWNED
    internal/angular/family identities is exact; no module is chosen by size.
    The geometric fermion density is N*C_rho*R^3, not the bosonic common
    pushforward weight. Its isometry only removes sqrt(C_rho*R^3).
    """
    G=np.asarray(gamma,complex);eps=int(sheet_orientation)
    if G.shape!=(5,4,4)or eps!=sheet_orientation or eps not in(-1,1)or not np.isfinite(G).all():raise ValueError('Owned Lorentz Spin4 five-gamma carrier and eta orientation required')
    metric=np.diag([1.,-1.,-1.,-1.,-1.]);I=np.eye(4,dtype=complex)
    defect=max(np.max(abs(G[a]@G[b]+G[b]@G[a]-2*metric[a,b]*I))for a in range(5)for b in range(5))
    adjoint=max(np.max(abs(G[a].conj().T-(G[a]if a==0 else-G[a])))for a in range(5))
    if max(defect,adjoint)>1e-11:raise ValueError('Declared (+----) Clifford/current adjoint convention required')
    N,dN=_value_and_first(c,'lapse');shape=N.shape
    C,dC=_value_and_first(c,'radial_coframe',shape);R,dR=_value_and_first(c,'radius',shape)
    z,dz=_value_and_first(c,'coordinate_shift',shape);f,df=_value_and_first(c,'eta_profile',shape)
    ft,dft=_value_and_first(c,'eta_profile_coordinate_time',shape);fr,dfr=_value_and_first(c,'eta_profile_radial',shape)
    if any(a.shape!=dN.shape for a in(dC,dR,dz,df,dft,dfr)):raise ValueError('One common explicit analytic source-first axis required')
    if any(np.any(v.imag!=0)for v in(N,C,R,z,f,ft,fr))or any(np.any(v.real<=0)for v in(N,C,R)):raise ValueError('Real regular positive coframe branch required; no complex.real projection')
    sine=np.sin(f)
    if np.any(abs(sine)<1e-14):raise ValueError('Polar sin(f)=0 requires the owned endpoint form domain')
    cot=np.cos(f)/sine;dcot=-df/sine**2
    f0=(ft-z*fr)/N;f4=fr/C
    df0=(dft-dz*fr-z*dfr)/N-f0*dN/N;df4=dfr/C-f4*dC/C
    a=f0*cot;da=df0*cot+f0*dcot;b=f4*cot;db=df4*cot+f4*dcot
    alpha4=G[0]@G[4];gammaE=G.copy();gammaE[1:]*=-1j;Uout=-1j*gammaE[0]
    formal=1j*a[:,None,None]*I+1j*eps*b[:,None,None]*alpha4
    native=-a[:,None,None]*I+1j*eps*b[:,None,None]*alpha4
    formal_first=1j*da[:,:,None,None]*I+1j*eps*db[:,:,None,None]*alpha4
    native_first=-da[:,:,None,None]*I+1j*eps*db[:,:,None,None]*alpha4
    etaE=-1j*cot[:,None,None]*(f0[:,None,None]*gammaE[0]+eps*f4[:,None,None]*gammaE[4])
    delta=-(1+1j)*a;ddelta=-(1+1j)*da
    mu=N*C*R**3;dmu=mu*(dN/N+dC/C+3*dR/R)
    rho_sqrt=np.sqrt(C*R**3);drho_sqrt=.5*rho_sqrt*(dC/C+3*dR/R)
    if 'volume_density'in c:
        supplied,dsupplied=_value_and_first(c,'volume_density',shape)
        if dsupplied.shape!=dmu.shape:raise ValueError('Fermion density source axes differ')
        density_defect=float(np.max(abs(supplied-mu)/np.maximum(1,abs(mu))))
        density_first_defect=float(np.max(abs(dsupplied-dmu)/np.maximum(1,abs(dmu))))
        if max(density_defect,density_first_defect)>1e-10:raise ValueError('The action-owned fermion density does not match N*C_rho*R^3')
    else:density_defect=density_first_defect=None
    return dict(gamma_E=gammaE,unitary_output_map=Uout,
        formal_eta_spin_body=formal,formal_eta_spin_body_first=formal_first,
        covector_native_eta_spin_body=native,covector_native_eta_spin_body_first=native_first,
        delta_scalar_body=delta,delta_scalar_body_first=ddelta,
        f_timelike_derivative=f0,f_timelike_derivative_first=df0,f_radial_derivative=f4,
        fermion_geometric_density=mu,fermion_geometric_density_first=dmu,
        input_output_density_isometry=rho_sqrt,input_output_density_isometry_first=drho_sqrt,
        Clifford_output_contact_identity_defect=float(np.max(abs(np.einsum('ij,qjk->qik',Uout,etaE)-native))),
        formal_to_native_contact_identity_defect=float(np.max(abs(native-formal-delta[:,None,None]*I))),
        supplied_fermion_density_scaled_defect=density_defect,supplied_fermion_density_first_scaled_defect=density_first_defect,
        real_positive_coframe_same_covector_connection_premise=True,
        new_Wick_contour_or_phase_selected=False,sin_f_removed_from_density=False,
        local_sin_f_similarity_is_unitary=False,full_AE4_graded_carrier_or_global_domain_identified=False,
        physical_native_energy_dictionary_identified=False)
