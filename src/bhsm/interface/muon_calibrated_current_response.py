"""Execute the matched hadronic two-current photon/Pauli application.

The electromagnetic current is j=sum Q_f qbar gamma q (e excluded).
R_bare=12*pi*Im(Pi). Its Thomson-subtracted transverse form therefore
has A0=Q^2 and R_ind=-Q^2*Delta_alpha_had(-Q^2). This is one measured
native sector, disjoint from the retained leptonic/local-Higgs ledger.
It does not replace the parent DtN or other native sectors by zero.
"""
from __future__ import annotations

import math
from functools import lru_cache
import numpy as np
from numpy.polynomial.legendre import leggauss

from .muon_calibrated_local_pauli import pauli_tensors, local_spin_pole_application
from .universal_precision_form_factor import project_electromagnetic_form_factors


DISPERSION_SOURCE = 'https://arxiv.org/abs/2112.05704'


@lru_cache(maxsize=12)
def _gauss_rule(order):
    return leggauss(order)


def transverse_current_response(Q_squared, delta_alpha_jet, *, J=1., L=1.,
                                J_dot=0., L_dot=0.):
    """Solve primal and two adjoints in a unit transverse polarization.

    The derivative here is Q^2, a physical photon momentum variable. It
    is NOT the external soft-transfer derivative. Momentum motion of J,L
    is retained in the identity. The perturbative Pauli consumer below
    takes one insertion, not the unexpanded resummed propagator.
    """
    Q=float(Q_squared)
    d,dd,ddd=map(float,delta_alpha_jet)
    if not np.isfinite([Q,d,dd,ddd]).all() or Q<=0:
        raise ValueError('finite positive Q_squared and a finite Q^2 jet required')
    if 1-d<=0:
        raise ValueError('resummed response outside the positive spacelike domain')
    J,L,J_dot,L_dot=map(complex,(J,L,J_dot,L_dot))
    A0=Q;R=-Q*d;A=A0+R
    A_dot=1-d-Q*dd; A_ddot=-2*dd-Q*ddd
    u0=J/A0;u=J/A;p=L/A0;z=L/A
    u_dot=(J_dot-A_dot*u)/A
    direct=np.conj(L_dot)*u+np.conj(L)*u_dot
    adjoint=np.conj(L_dot)*u+np.conj(z)*(J_dot-A_dot*u)
    returned=np.conj(L)*(u-u0)
    reduced=-np.conj(p)*R*u
    one_insertion=-np.conj(p)*R*u0
    return dict(A0=A0,R_ind=R,A=A,A_Q_squared=A_dot,A_Q_squared_squared=A_ddot,
        J=J,L=L,u0=u0,u=u,p=p,z=z,
        primal_residual=abs(A*u-J),reference_adjoint_residual=abs(A0*p-L),
        full_adjoint_residual=abs(A*z-L),
        returned_response=returned,reduced_response=reduced,
        return_identity_residual=abs(returned-reduced),
        dimensionless_return_identity_residual=Q*abs(returned-reduced),
        full_derivative=adjoint,direct_derivative=direct,
        derivative_identity_residual=abs(adjoint-direct),
        first_insertion_return=one_insertion,
        first_insertion_dimensionless_return=Q*one_insertion,
        derivative_parameter='internal spacelike photon Q^2, not external soft transfer',
        normalization='unit transverse polarization, charge-normalized external currents',
        perturbative_consumer='one hadronic VP insertion only',
        whole_native_evaluated=False)


def _finite_transfer_average(k):
    """int_0^1 du/[1+k*u*(1-u)] with a stable removable origin."""
    k=np.asarray(k,float)
    result=np.empty_like(k);small=k<1e-4
    a=k[small]
    result[small]=1-a/6+a*a/30-a**3/140+a**4/630
    a=k[~small]
    result[~small]=2*np.arcsinh(np.sqrt(a)/2)/(np.sqrt(a)*np.sqrt(1+a/4))
    return result


def finite_transfer_pauli_kernel(s, mass_GeV, rho, *, order=96):
    """Actual massive-photon vertex kernel at Q_ext^2/m^2=rho>=0.

    After Feynman parametrization beta+gamma=x, gamma=x*u, the Pauli
    numerator is x^2*(1-x). The denominator is x^2+(1-x)*s/m^2+
    rho*x^2*u*(1-u). Charge/LSZ counterterms have the Dirac tensor.
    For a positive spectrum, 0<=F2(0)-F2(rho)<=rho*F2(0)/6.
    This is a soft-limit bound, not a spectral or full-native enclosure.
    """
    s=np.asarray(s,float);m=float(mass_GeV);rho=float(rho)
    if m<=0 or rho<0 or np.any(s<0) or not np.isfinite(s).all() or not np.isfinite([m,rho]).all():
        raise ValueError('finite s>=0, m>0, rho>=0 required')
    # The photon-mass endpoint layer has width O(m^2/s). Resolve it in
    # the integration partition rather than trusting a fixed uniform
    # Gauss grid at arbitrarily large s. Each interval is integrated with
    # the requested order; repeated endpoints have zero measure.
    z,w=_gauss_rule(order)
    q=(s/m**2).ravel();result=np.empty_like(q)
    for start in range(0,len(q),256):
        v=q[start:start+256]
        knots=np.stack((np.zeros_like(v),.5*np.ones_like(v),
            np.maximum(.5,1-1/np.sqrt(1+v)),
            np.maximum(.5,1-1/(1+v)),np.ones_like(v)),axis=-1)
        left=knots[...,:-1,None];width=np.diff(knots,axis=-1)[...,None]
        x=left+width*(z+1)/2
        denominator=x*x+(1-x)*v[...,None,None]
        result[start:start+len(v)]=np.sum(width*w/2*x*x*(1-x)/denominator*
            _finite_transfer_average(rho*x*x/denominator),axis=(-2,-1))
    return result.reshape(s.shape)


def spectral_soft_pauli_application(spectrum, *, alpha, mass_GeV, t, direction,
                                    spectral_order=20, kernel_order=128):
    """Execute the spectral vertex then the existing signed Pauli readout.

    The scalar multiplying the Pauli tensor is integrated from R_bare;
    no anomaly target or free Pauli coefficient is used. Finite Breit
    external momenta stay on the measured local mass shell. The covariant
    tensor representative already contains their motion, once.
    """
    from .muon_calibrated_hvp_spectral import integrate_spectral_kernel, leading_hvp_pauli
    u=np.asarray(direction,float);a=float(alpha);m=float(mass_GeV);t=float(t)
    if u.shape!=(3,) or np.linalg.norm(u)==0 or t==0 or a<=0 or m<=0 or not np.isfinite(u).all():
        raise ValueError('finite nonzero spatial direction/t and positive alpha/mass required')
    rho=t*t*float(u@u);pref=a*a/(3*math.pi**2)
    kernel=lambda s:finite_transfer_pauli_kernel(s,m,rho,order=kernel_order)
    finite=integrate_spectral_kernel(spectrum,lambda s:pref*kernel(s)/s,order=spectral_order)
    zero=leading_hvp_pauli(spectrum,a,m,order=spectral_order)
    q=np.r_[0.,t*m*u];D,P=pauli_tensors(q,m)
    _,Pu=pauli_tensors(np.r_[0.,m*u],m)
    perpendicular=Pu-D*np.vdot(D.ravel(),Pu.ravel())/np.vdot(D.ravel(),D.ravel()).real
    Lu=perpendicular/np.vdot(perpendicular.ravel(),perpendicular.ravel()).real
    delta=P*finite['value']
    derivative=np.vdot(Lu.ravel(),delta.ravel())/t
    projected=project_electromagnetic_form_factors(D+delta,D,P,q_squared=-float(q[1:]@q[1:]))
    return dict(t=t,direction=u.tolist(),rho=rho,F2_finite=finite['value'],F2_zero=zero['value'],
        signed_soft_derivative=derivative,soft_bias_bound=rho*zero['value']/6,
        actual_soft_difference=abs(derivative-zero['value']),
        Dirac_annihilation_residual=abs(np.vdot(Lu.ravel(),D.ravel())),
        Pauli_unit_pairing_residual=abs(np.vdot(Lu.ravel(),Pu.ravel())-1),
        form_factor_projection_residual=projected.relative_projection_residual,
        F1=projected.F1,F2=projected.F2,
        local_external_pole=local_spin_pole_application(m,float(np.linalg.norm(q[1:]))/2),
        spectral_error=zero['spectral_error'],source=DISPERSION_SOURCE,
        subtraction='Pi(0)=0; hadronic two-current sector absent from preserved leptonic QED/Higgs subtotal',
        action_selected=False,Gate7_closed=False,whole_native_evaluated=False,
        error_scope='spectral uncertainty plus soft bound; quadrature/continuum and other sectors separate')


def magnetic_moment_accounting(*, a_mu, mass_GeV, charge_sign):
    """mu_vector=g*q/(2m)*S; for S_z=+hbar/2 return signed J/T.

    No magnetic-moment measurement is used. SI h,c,e are exact; the mass
    is the optical/spectroscopic calibrated mass, not a spin-precession
    mass extraction. This arithmetic does not certify completeness of a.
    """
    if charge_sign not in (-1,1) or mass_GeV<=0 or not np.isfinite([a_mu,mass_GeV]).all():
        raise ValueError('finite a_mu, mass>0, charge_sign +/-1 required')
    h=6.62607015e-34;c=299792458.;e=1.602176634e-19
    mass_kg=mass_GeV*(e*1e9)/(c*c)
    magneton=e*(h/(2*math.pi))/(2*mass_kg)
    g=2*(1+a_mu)
    return dict(a_mu=float(a_mu),g_mu=g,charge_sign=charge_sign,
        muon_magneton_J_per_T=magneton,
        magnetic_moment_Sz_plus_hbar_over_2_J_per_T=charge_sign*(1+a_mu)*magneton,
        da_to_dg=2.,da_to_dmoment_J_per_T=charge_sign*magneton,
        dmass_to_dmoment_J_per_T_per_GeV=-charge_sign*(1+a_mu)*magneton/mass_GeV,
        sign_convention='mu=g*q*S/(2m); positive spin projection; q=charge_sign*e',
        completeness_determined_by_contribution_ledger=True)


def paired_two_current_pauli(spectrum, *, alpha, muon_mass_GeV, electron_mass_GeV,
                            spectral_order=20):
    """Evaluate the same current on both lepton mass shells with shared errors.

    The finite hadronic two-current diagrams have no local leptonic/Higgs
    overlap. The electron subtraction is a paired diagnostic: the muon
    contribution remains a_mu_had, not a_mu_had-a_e_had. No heat or complete
    stratified-family equality is inferred from this direct current route.
    """
    from .muon_calibrated_hvp_spectral import leading_hvp_pauli
    muon=leading_hvp_pauli(spectrum,alpha,muon_mass_GeV,order=spectral_order)
    electron=leading_hvp_pauli(spectrum,alpha,electron_mass_GeV,order=spectral_order)
    rows={}
    for name in ('statistical','systematic'):
        m=np.asarray(muon[name+'_error_vector']);e=np.asarray(electron[name+'_error_vector'])
        if m.shape!=e.shape:
            raise ArithmeticError('paired currents must retain the same spectral uncertainty rows')
        rows[name]=(m-e).tolist()
    delta=muon['value']-electron['value']
    return dict(muon=muon,electron=electron,muon_minus_electron=delta,
        difference_error_vectors=rows,
        difference_source_standard_uncertainty=float(math.sqrt(sum(np.dot(v,v) for v in rows.values()))),
        family_pairing='same bare electromagnetic current and physical charge normalization; separate measured pole masses',
        muon_consumer='use the muon value; difference is not substituted for the muon anomaly',
        overlap_with_preserved_local=0.,overlap_zero_provenance='hadronic current sector absent from retained local leptonic/Higgs diagrams',
        completed_native_pair=False)
