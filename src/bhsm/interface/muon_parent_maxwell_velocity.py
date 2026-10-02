"""Current-C2 predecessor Maxwell velocity density, with matching explicit.

This muon realization does not implement the full AE4 induced Hessian.
Results are factored by kappa1 and by the component-to-Q attachment index.
No reference cap radius, gauge calibration, mode count or family count is
inserted into the computed density.
"""
from __future__ import annotations
import numpy as np


class MissingConnectionAttachment(ValueError):
    pass


def current_parent_fields(states, log_R4, rho, *, order=12):
    """Reconstruct the supplied Galerkin parent using the saved physical R4.

    rho=2 chi. Layout: (q,velocity,lapse/shift), len(q)=1+3*order.
    Rcap is obtained from R4 and the current boundary u,v, rather than the
    historical RADIUS0 constant. Shift is expressed in boundary proper time.
    No positive heat-metric/domain matching is supplied by this function.
    """
    y=np.asarray(states,float)
    x=np.asarray(log_R4,float)
    rho=np.asarray(rho,float)
    qdim=1+3*order
    if (y.ndim!=2 or y.shape[1]!=2*qdim+2*order or x.shape!=(len(y),)
        or rho.ndim!=1 or np.any(rho<0) or np.any(rho>np.pi/2)
        or not np.isfinite(y).all() or not np.isfinite(x).all()):
        raise ValueError('matching finite C2 states, boundary log radius and cap coordinates required')
    q=y[:,:qdim]; m=y[:,2*qdim:]
    k=np.arange(1,order+1); j=np.arange(order)
    chi=rho/2
    ck=np.cos(np.outer(chi,4*k)); cj=np.cos(np.outer(chi,4*j))
    window=np.sin(2*chi)**2
    u=q[:,1:1+order]@ck.T
    w=(q[:,1+order:1+2*order]@cj.T)*window
    v=(q[:,1+2*order:1+3*order]@cj.T)*window
    ub=q[:,1:1+order]@((-1.)**k)
    vb=q[:,1+2*order:1+3*order]@((-1.)**j)
    R4=np.exp(x)
    Rcap=2*R4*np.exp(-ub)*np.sqrt(np.cosh(2*vb))
    Cchi=Rcap[:,None]*np.exp(u+w)
    A=Rcap[:,None]*np.exp(u+v)*np.cos(chi)
    B=Rcap[:,None]*np.exp(u-v)*np.sin(chi)
    LF=np.sqrt(A*A+B*B)
    r=A*B/LF
    logN=m[:,:order]@ck.T
    logNb=m[:,:order]@((-1.)**k)
    N=np.exp(logN); Nb=np.exp(logNb)
    nu=np.exp(logN-logNb[:,None])
    shift_chi=np.sin(4*chi)*(m[:,order:]@cj.T)
    shift_rho_proper=2*shift_chi/Nb[:,None]
    sigma=-.5+rho/np.pi-np.sin(2*rho)/(2*np.pi)
    Lambda=1-4*sigma*sigma
    return dict(A=A,B=B,C_rho=Cchi/2,base_radius=r,fiber_radius=LF,
        raw_lapse=N,boundary_lapse=Nb,proper_lapse=nu,
        raw_shift_chi=shift_chi,proper_shift_rho=shift_rho_proper,
        boundary_radius=R4,parent_scale=Rcap,Lambda=Lambda,rho=rho,
        connection_component_coefficient_per_kappa1=np.pi**2*LF**5)


def local_velocity_density(fields, *, angular_haar_Gram):
    """Geometric predecessor velocity Hessian per kappa1 and Q index.

    Unit S3 angular volume is 2*pi²; the saved modes are Haar normalized.
    The scalar factor follows from radial ADM geometry and the angular
    metric being round, not from curl²=9. A supplied dense Gram is retained.
    K_Q/kappa1=(pi² LF^5)*c_Q, c_Q=Tr16(Q²)/I_embedding.
    Returned b coefficients are densities in rho and boundary proper time.
    The physical component/Tr16 attachment and AE4 remainder are unevaluated
    and have not been set to zero.
    """
    gram=np.asarray(angular_haar_Gram,complex)
    if gram.shape!=(8,8) or not np.allclose(gram,gram.conj().T,atol=1e-13):
        raise ValueError('eight-mode Hermitian Haar Gram required')
    K=fields['connection_component_coefficient_per_kappa1']
    W=fields['Lambda'][None]
    C,r,nu=(fields[name] for name in ('C_rho','base_radius','proper_lapse'))
    Rb=fields['boundary_radius'][:,None]
    beta_scalar=2*np.pi**2*K*W*C*r/nu
    # beta=(R4*f_R4)*b = b/sqrt(2*pi²*R4), so pull back once.
    b_scalar=K*W*C*r/(nu*Rb)
    radial_b=K*W*nu*r/(C*Rb)
    return dict(beta_velocity_density_per_kappa1_cQ=beta_scalar,
                b_velocity_density_per_kappa1_cQ=b_scalar,
                b_radial_density_per_kappa1_cQ=radial_b,
                beta_velocity_matrix_per_kappa1_cQ=beta_scalar[:,:,None,None]*gram,
                b_velocity_matrix_per_kappa1_cQ=b_scalar[:,:,None,None]*gram,
                actual_angular_Haar_Gram=gram)


def electromagnetic_trace_coefficient(K_component, *, embedding_index=None):
    """Ordinary one-family Tr16(Q²)=16/3, attached exactly once.

    I is defined by Tr16(jmath(L_a)^dagger jmath(L_b))=I delta_ab
    for the SAME mechanical component basis and connection amplitude.
    Specifying an unrelated trace convention does not define jmath.
    """
    if embedding_index is None:
        raise MissingConnectionAttachment(
            'jmath: mechanical Sp(1) connection components -> retained '
            'rank16 neutral gauge connection; I_jmath and U(1) attachment '
            'must be matched to the same action')
    index=float(embedding_index)
    if not np.isfinite(index) or index<=0:
        raise ValueError('positive action-derived embedding index required')
    return np.asarray(K_component)*(16/3)/index


def temporal_and_radial_flux(b,d_tau_b,d_rho_b, *, e,r,shift,H,
                            radial_form_sign):
    """Both fluxes come from one local bilinear; epsilon preserves its sign.

    L=1/2[e |D b|² + epsilon*r |b_rho|²]+other same-action terms.
    D b=b_tau-shift*b_rho-H*b/2.
    Lorentz Maxwell L has epsilon=-1. A positive spatial form has +1
    only where the retained positive realization establishes that matching.
    This helper makes no choice of positive realization or endpoint domain.
    """
    if radial_form_sign not in (-1,1):
        raise ValueError('the owned radial-form sign must be supplied')
    normal=d_tau_b-shift*d_rho_b-.5*H*b
    pi_tau=e*normal
    pi_rho=-shift*pi_tau+radial_form_sign*r*d_rho_b
    return pi_tau,pi_rho
