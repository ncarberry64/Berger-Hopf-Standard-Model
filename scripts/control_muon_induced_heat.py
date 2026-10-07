"""Three-dimensional arithmetic CONTROL, never a native operator model.

One common D generates all jets. Explicit control ell=0.7 (not physical).
Tests signed mixed contacts, noncommuting jets and moving M using the
existing Arb HeatPencil. No BHSM physical input is replaced by this block.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import quad
from scipy.linalg import expm, expm_frechet
from bhsm.interface.muon_native_induced_polarization import generalized_form_jets


def control_data():
    D=np.diag([1.,1.5,2.])
    v=np.outer([.2,-.1,.3],[.1,.4,-.2])
    j=np.outer([-.1,.2,.15],[.3,-.2,.1])
    vj=np.outer([.01,.02,-.01],[.1,-.2,.3])
    M=np.array([[1.2,.1,0],[.1,1.1,.04],[0,.04,.9]])
    Mv=np.diag([.02,-.01,.03]);Mj=np.array([[0,.01,0],[.01,.02,0],[0,0,-.01]])
    Mvj=np.diag([.003,.002,-.001])
    return D,v,j,vj,M,Mv,Mj,Mvj


def execute_control():
    from flint import arb_mat,ctx
    from bhsm.interface.arb_heat_pencil_contractions import HeatPencil
    D,v,j,vj,M,Mv,Mj,Mvj=control_data()
    ell=.7;c=ell**2;zero=np.zeros_like(M)
    fixed=generalized_form_jets(D,v,j,vj,np.eye(3),zero,zero,zero)
    P,V,J,C=[fixed[k] for k in ('A','A_v','A_J','A_vJ')]
    lam,U=np.linalg.eigh(P);q=np.exp(-c*lam)/(2*lam)
    qp=-np.exp(-c*lam)*(c/lam+1/lam**2)/2
    dd=np.array([[qp[i] if i==k else (q[i]-q[k])/(lam[i]-lam[k])
                  for k in range(3)] for i in range(3)])
    dense_contact=float(np.sum(q*np.diag(U.T@C@U)))
    dense_pair=float(np.sum(dd*(U.T@J@U)*(U.T@V@U).T))
    E=expm(-c*P);dE=expm_frechet(-c*P,-c*J,compute_expm=False)
    Q=np.linalg.solve(P.T,E.T).T/2
    dQ=np.linalg.solve(P.T,(dE/2-Q@J).T).T
    block_value=float(np.trace(Q@C+dQ@V))
    # Factor only the supplied CONTROL jets; no native finite-rank assertion.
    ve,vu=np.linalg.eigh(V);je,ju=np.linalg.eigh(J);ce,cu=np.linalg.eigh(C)
    def factor_contact(t):
        H=expm(-t*P)
        return sum(ce[a]*(cu[:,a]@H@cu[:,a]) for a in range(3))/2
    def factor_pair(t,u):
        HL=expm(-(t-u)*P);HR=expm(-u*P)
        return sum(ve[a]*je[b]*(ju[:,b]@HL@vu[:,a])*
                   (vu[:,a]@HR@ju[:,b]) for a in range(3) for b in range(3))/2
    contact,contact_err=quad(factor_contact,c,np.inf,epsabs=2e-12,epsrel=2e-12)
    # Exact finite-dimensional spectral identity for the inner convolution;
    # the outer integral is an independent proper-time quadrature.
    Vm=U.T@V@U;Jm=U.T@J@U
    def integrated_pair(t):
        weights=np.array([[t*np.exp(-t*lam[i]) if i==k else
                    (np.exp(-t*lam[k])-np.exp(-t*lam[i]))/(lam[i]-lam[k])
                    for k in range(3)] for i in range(3)])
        return float(np.sum(weights*Vm*Jm.T))/2
    pair,pair_err=quad(integrated_pair,c,np.inf,epsabs=2e-12,epsrel=2e-12)
    # One actual rank-factorized inner application, compared to dense trace.
    t=.9;u=.3
    fact=factor_pair(t,u)
    direct=float(np.trace(expm(-(t-u)*P)@V@expm(-u*P)@J))/2
    moving=generalized_form_jets(D,v,j,vj,M,Mv,Mj,Mvj)
    def arb_value(jets,m,mv,mj,mvj):
        with ctx.workprec(192):
            a=lambda x:arb_mat(np.asarray(x).tolist())
            h=HeatPencil(a(jets['K']),a(m),heat_length=ell)
            ans=h.mixed(a(jets['K_v']),a(mv),a(jets['K_J']),a(mj),a(jets['K_vJ']),a(mvj))
            return str(ans['value']),float(ans['value'].mid()),float(ans['value'].rad().upper())
    fixed_interval,fixed_value,fixed_rad=arb_value(fixed,np.eye(3),zero,zero,zero)
    moving_interval,moving_value,moving_rad=arb_value(moving,M,Mv,Mj,Mvj)
    # Independent noncommuting block-exponential calculation for moving M.
    A,Av,Aj,Avj=[moving[k] for k in ('A','A_v','A_J','A_vJ')]
    E=expm(-c*A);dE=expm_frechet(-c*A,-c*Aj,compute_expm=False)
    Q=np.linalg.solve(A.T,E.T).T/2
    dQ=np.linalg.solve(A.T,(dE/2-Q@Aj).T).T
    moving_dense=float(np.trace(dQ@Av+Q@Avj))
    return dict(classification='ARITHMETIC_CONTROL_ONLY',dimension=3,
        control_ell=ell,physical_ell_assigned=False,
        all_jets_from_one_D=True,nonzero_D_vJ_norm=float(np.linalg.norm(vj)),
        fixed_dense_contact=dense_contact,fixed_dense_pair=dense_pair,
        fixed_dense_value=dense_contact+dense_pair,
        fixed_block_value=block_value,proper_time_contact=contact,
        proper_time_pair=-pair,proper_time_value=contact-pair,
        scipy_quadrature_estimate_not_certified=contact_err+pair_err,
        rank_factor_application_residual=abs(fact-direct),
        Arb_fixed_interval=fixed_interval,Arb_fixed_midpoint=fixed_value,
        Arb_fixed_radius=fixed_rad,Arb_moving_interval=moving_interval,
        Arb_moving_midpoint=moving_value,Arb_moving_radius=moving_rad,
        moving_dense_value=moving_dense,
        moving_two_mass_terms_retained=True,
        max_fixed_method_difference=max(abs(x-(dense_contact+dense_pair)) for x in
            (block_value,contact-pair,fixed_value)),
        moving_method_difference=abs(moving_value-moving_dense),
        native_grading_quotient_domain_tails_supplied=False)
