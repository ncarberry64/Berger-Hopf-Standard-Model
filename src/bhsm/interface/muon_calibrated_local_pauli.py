"""Numerical on-shell LOCAL QED Pauli applications with measured matching.

The retained minimal charged-lepton/photon action, canonically matched to
the Thomson charge and pole masses, has the ordinary local QED diagrams.
Their finite Pauli projection is reused through order alpha**2.  Native
heat, its overlap subtraction, weak/strong terms and higher local orders
are NOT supplied by this calculation.  No BHSM promotion flag is raised.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.integrate import quad
from scipy.special import zeta

from .ae31_c2_local_em_ward_identity import _gamma_matrices
from .universal_quadratic_spectrum import QuadraticDescriptorPencil
from .universal_lsz import normalize_simple_pole
from .universal_precision_form_factor import project_electromagnetic_form_factors


SCHWINGER_SOURCE='https://doi.org/10.1103/PhysRev.73.416'
SPACELIKE_INTEGRAL_SOURCE='https://doi.org/10.1103/PhysRevD.108.096036'
UNIVERSAL_TWO_LOOP_SOURCE='https://doi.org/10.1103/PhysRev.107.328'
MASS_DEPENDENT_LEDGER_SOURCE='https://arxiv.org/abs/1205.5370'


def local_spin_pole_application(mass_GeV,spatial_momentum_GeV,*,spin=1):
    """Actually solve the matched free Dirac spin-sector pole and residue.

    This is the local quadratic symbol in a spin sector commuting with the
    free Hamiltonian, not an arbitrary full BHSM external-mode selection.
    Physical self-energy derivatives/native-mode mixing remain separate.
    The spin degeneracy of the 4x4 symbol is not mislabeled a simple pole.
    """
    m=float(mass_GeV);p=float(spatial_momentum_GeV)
    if not np.isfinite([m,p]).all() or m<=0 or spin not in (-1,1):
        raise ValueError('positive pole mass, finite collinear momentum and spin +/-1 required')
    K0=np.array([[-m,-spin*p],[spin*p,-m]],complex)
    K1=np.diag([1.,-1.]).astype(complex)
    pencil=QuadraticDescriptorPencil(K0,K1,'BHSM-AE-3.1.0',
        'CALIBRATED_LOCAL_ON_SHELL_QUADRATIC_SYMBOL',
        'one commuting free spin sector',False,True,False,None)
    poles=pencil.poles_and_residues()
    positive=next(x for x in poles if x.spectral_parameter.real>0)
    mode=normalize_simple_pole(positive,K1,mode_id=f'calibrated_local_muon_spin_{spin}',
        action_selected=False,provenance=('measured pole matching; original fixed-family operator unchanged',))
    return dict(energy_GeV=positive.spectral_parameter.real,
        analytic_energy_GeV=math.hypot(m,p),right_mode=mode.right_mode,left_mode=mode.left_mode,
        residue=positive.residue,
        pole_residual=float(np.linalg.norm(pencil.symbol(positive.spectral_parameter)@mode.right_mode)),
        LSZ_descriptor_residual=mode.descriptor_normalization_residual,
        simple_within_spin_sector=positive.simple,
        full_spin_degeneracy=2,action_selected=False,Gate7_closed=False,
        interacting_BHSM_LSZ_evaluated=False,
        normalization_scope='local on-shell matched quadratic symbol only')


def pauli_tensors(transfer_GeV,mass_GeV):
    """Retained +--- gamma convention, physical mass in P=i sigma q/(2m)."""
    q=np.asarray(transfer_GeV,float);m=float(mass_GeV)
    if q.shape!=(4,) or not np.isfinite(q).all() or m<=0:raise ValueError('finite q and positive mass required')
    gamma=np.asarray(_gamma_matrices());qc=q*np.array([1,-1,-1,-1])
    P=np.zeros_like(gamma)
    for mu in range(4):
        for nu in range(4):
            sigma=.5j*(gamma[mu]@gamma[nu]-gamma[nu]@gamma[mu])
            P[mu]+=1j*sigma*qc[nu]/(2*m)
    return gamma,P


def one_loop_pauli_spacelike(*,alpha,Q_squared_over_m_squared,epsabs=1e-12):
    """Finite on-shell vertex Pauli integral after its QED tensor reduction.

    F2(-Q²)=alpha/(2pi) integral_0^1 du/[1+(Q²/m²)u(1-u)].
    The UV/IR singular Dirac piece is absent from this transverse scalar;
    on-shell charge and residue counterterms multiply the Dirac tensor.
    This does not assert cancellation of an unevaluated native remainder.
    """
    a=float(alpha);rho=float(Q_squared_over_m_squared)
    if not np.isfinite([a,rho]).all() or a<=0 or rho<0:raise ValueError('positive alpha and spacelike transfer required')
    value,error=quad(lambda u:1/(1+rho*u*(1-u)),0,1,epsabs=epsabs,epsrel=epsabs)
    pref=a/(2*math.pi)
    return dict(F2=pref*value,quadrature_error_estimate=pref*error,
        soft_bias_bound=pref*rho/6,
        exact_zero_limit=pref,source=SCHWINGER_SOURCE,
        finite_transfer_source=SPACELIKE_INTEGRAL_SOURCE,finite_transfer_equations='33-34; spacelike substitution',
        scope='LOCAL_ON_SHELL_QED_ONE_LOOP',native_evaluated=False)


def signed_soft_transfer_application(*,alpha,mass_GeV,t,direction):
    """Calculate the existing projected scalar derivative at signed t.

    Breit momenta (E,-q/2),(E,+q/2) have the calibrated mass shell;
    the covariant representative avoids adding external spinor derivatives
    twice.  This is the calculated local loop part of the quantum vertex.
    """
    u=np.asarray(direction,float)
    if u.shape!=(3,) or not np.isfinite(u).all() or np.linalg.norm(u)==0 or t==0:
        raise ValueError('nonzero spatial direction and signed nonzero transfer required')
    q=np.concatenate(([0.],float(t)*float(mass_GeV)*u))
    D,P=pauli_tensors(q,mass_GeV);_,Pu=pauli_tensors(np.concatenate(([0.],mass_GeV*u)),mass_GeV)
    dp=np.vdot(D.ravel(),Pu.ravel());dd=np.vdot(D.ravel(),D.ravel()).real
    perp=Pu-D*dp/dd;L=perp/np.vdot(perp.ravel(),perp.ravel()).real
    integral=one_loop_pauli_spacelike(alpha=alpha,Q_squared_over_m_squared=t*t*float(u@u))
    delta=P*integral['F2'] # a derived loop scalar, not a supplied synthetic coefficient
    derivative=np.vdot(L.ravel(),delta.ravel())/t
    projection=project_electromagnetic_form_factors(D+delta,D,P,q_squared=-float(q[1:]@q[1:]))
    external=local_spin_pole_application(mass_GeV,float(np.linalg.norm(q[1:]))/2)
    return dict(t=float(t),direction=u,projected_derivative=derivative,
        exact_one_loop_limit=integral['exact_zero_limit'],soft_bias_bound=integral['soft_bias_bound'],
        quadrature_error_estimate=integral['quadrature_error_estimate'],
        absolute_limit_difference=float(abs(derivative-integral['exact_zero_limit'])),
        Dirac_annihilation_residual=float(abs(np.vdot(L.ravel(),D.ravel()))),
        Pauli_unit_pairing_residual=float(abs(np.vdot(L.ravel(),Pu.ravel())-1)),
        form_factor_projection_residual=projection.relative_projection_residual,
        F1=projection.F1,F2=projection.F2,local_external_pole=external,
        physical_native_promotion=False)


def universal_two_loop_coefficient():
    """Exact on-shell mass-independent seven-diagram coefficient."""
    return 197/144+math.pi**2/12+3*zeta(3,1)/4-math.pi**2*math.log(2)/2


def lepton_vacuum_polarization_pauli(mass_ratio,*,eps=2e-10):
    """Execute the on-shell subtracted one-loop VP insertion scalar.

    A2^(4)(r)=2 int dx(1-x) int dy y(1-y)
                      log[1+r² x² y(1-y)/(1-x)].
    Pi(0)=0 is the Thomson subtraction, not a fitted correction.  The
    muon-loop term belongs to A1; call this for electron and tau only.
    """
    r=float(mass_ratio);tolerance=float(eps)
    if not np.isfinite(r) or r<=0:raise ValueError('positive pole-mass ratio required')
    if not np.isfinite(tolerance) or tolerance<=0:
        raise ValueError('positive finite numerical quadrature tolerance required')
    r2=r*r
    if not math.isfinite(r2):raise ValueError('finite squared pole-mass ratio required')
    # I(k)=2 int y(1-y) log(1+k y(1-y)) dy.  For k>=1 use its
    # elementary antiderivative, with L=2 asinh(sqrt(k)/2) avoiding
    # cancellation in log((v+1)/(v-1)) at large k.  Below k=1 the
    # cancellation of 1/k terms is avoided by the convergent beta series
    # I(k)=2 sum (-1)^(n+1) k^n B(n+2,n+2)/n.
    # d I/d log(r)=2k I'(k), not a finite difference in the input mass.
    series_terms=32
    def inner(k,derivative=False):
        if k<1:
            term=k/15;terms=[]
            for n in range(1,series_terms+1):
                terms.append(2*n*term if derivative else term)
                term*=-k*n*(n+2)**2/((n+1)*(2*n+5)*(2*n+4))
            return math.fsum(terms)
        v=math.sqrt(1+4/k);L=2*math.asinh(math.sqrt(k)/2)
        if derivative:return 2/3-4/k+8*L/(k*k*v)
        return 4/(3*k)-5/9+(1-2/k)*v*L/3
    def outer(x,derivative=False):
        if x==1:return 0.
        return (1-x)*inner(r2*x*x/(1-x),derivative)
    # Split at the representation switch k=1.  This is a quadrature
    # partition, not an approximation to or cutoff on the physical integral.
    split=2/(1+math.sqrt(1+4*r2))
    kwargs=dict(epsabs=tolerance,epsrel=tolerance,limit=200,points=[split])
    value,error=quad(outer,0,1,**kwargs)
    derivative,de=quad(lambda x:outer(x,True),0,1,**kwargs)
    # The alternating terms decrease for 0<=k<=1.  The next term bounds
    # their exact-arithmetic remainder, and int(1-x)dx=1/2.  This bound
    # covers series truncation only; it does not enclose floating roundoff.
    from fractions import Fraction
    n=series_terms+1
    beta=Fraction(math.factorial(n+1)**2,math.factorial(2*n+3))
    series_tail=np.nextafter(float(beta/n),math.inf)
    derivative_tail=np.nextafter(float(2*beta),math.inf)
    return dict(coefficient=value,derivative_log_mass_ratio=derivative,
        quadrature_error_estimate=error+series_tail,
        derivative_error_estimate=de+derivative_tail,mass_ratio=r,
        numerical_method='analytic VP inner integral; stable beta series and one adaptive outer integral',
        series_terms=series_terms,series_switch_k=1.,
        integrated_series_truncation_bound=series_tail,
        integrated_derivative_series_truncation_bound=derivative_tail,
        error_scope='QUADPACK outer error estimate plus exact-arithmetic series truncation bound; binary64 roundoff is not enclosed',
        rigorous_quadrature_enclosure=False,
        vacuum_polarization_integral_source='https://arxiv.org/abs/2210.11071',
        vacuum_polarization_equations='14-15 and36',
        source=MASS_DEPENDENT_LEDGER_SOURCE,scope='LOCAL_QED_TWO_LOOP_LEPTON_VP_ONLY')


def calibrated_local_qed_two_loop(*,alpha,muon_electron_ratio,muon_tau_ratio,eps=2e-13):
    """Recompute complete local-QED order alpha/alpha², preserving ledger."""
    electron=lepton_vacuum_polarization_pauli(muon_electron_ratio,eps=eps)
    tau=lepton_vacuum_polarization_pauli(muon_tau_ratio,eps=eps)
    x=float(alpha)/math.pi;A1=universal_two_loop_coefficient()
    terms=dict(local_QED_one_loop=x/2,
        local_QED_two_loop_mass_independent=x*x*A1,
        local_QED_two_loop_electron_VP=x*x*electron['coefficient'],
        local_QED_two_loop_tau_VP=x*x*tau['coefficient'])
    partial=sum(terms.values())
    return dict(contributions=terms,a_mu_local_QED_through_two_loops=partial,
        g_mu_local_QED_through_two_loops=2*(1+partial),
        coefficient_two_loop=A1+electron['coefficient']+tau['coefficient'],
        electron_VP_application=electron,tau_VP_application=tau,
        derivative_alpha=(.5+2*x*(A1+electron['coefficient']+tau['coefficient']))/math.pi,
        derivative_log_muon_electron_ratio=x*x*electron['derivative_log_mass_ratio'],
        derivative_log_muon_tau_ratio=x*x*tau['derivative_log_mass_ratio'],
        quadrature_error_estimate=x*x*(electron['quadrature_error_estimate']+tau['quadrature_error_estimate']),
        perturbative_truncation_bound=None,native_remainder=None,
        weak_and_strong_accounted=False,full_a_mu=None,full_g_mu=None,
        measured_anomaly_used=False,action_selected=False,Gate7_closed=False,
        scope='CALIBRATED_LOCAL_QED_COMPONENT_ONLY; not a completed BHSM prediction')


def fixed_yukawa_higgs_pauli(*,muon_mass_GeV,higgs_mass_GeV):
    """Local neutral radial Higgs loop using the retained FIXED Y_mu.

    H=(0,(v+h)/sqrt(2)) gives g_hmu=Y_mu/sqrt(2), not m_mu/v
    independently fitted from the measured pole.  The on-shell scalar
    integral is Eq.(35)/(64) of arXiv:1403.2309 with the same muon inside
    and outside the loop.  This is one local diagram and not native heat.
    """
    from .ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
    m=float(muon_mass_GeV);mh=float(higgs_mass_GeV)
    if not np.isfinite([m,mh]).all() or min(m,mh)<=0:
        raise ValueError('positive calibrated pole masses required')
    y=float(charged_lepton_yukawa_operator()['eigenvalues_heavy_middle_light'][1])
    g=y/math.sqrt(2);r2=(mh/m)**2
    integral,error=quad(lambda x:x*x*(2-x)/(x*x+(1-x)*r2),0,1,
        points=[1-1/r2] if r2>1 else None,epsabs=2e-14,epsrel=2e-12,limit=300)
    pref=g*g/(8*math.pi**2);value=pref*integral
    derivative,derivative_error=quad(lambda x:2*r2*x*x*(2-x)*(1-x)/(x*x+(1-x)*r2)**2,
        0,1,points=[1-1/r2] if r2>1 else None,epsabs=2e-14,epsrel=2e-12,limit=300)
    leading=pref/r2*(math.log(r2)-7/6)
    return dict(a_mu_local_radial_Higgs_one_loop=value,
        fixed_Y_mu=y,radial_scalar_coupling=g,
        independent_Y_mu_fitted=False,measured_muon_mass_used_only_as_pole=True,
        integral=integral,quadrature_error_estimate=pref*error,
        derivative_log_muon_mass=pref*derivative,derivative_log_higgs_mass=-pref*derivative,
        derivative_quadrature_error_estimate=pref*derivative_error,
        heavy_mass_asymptotic=leading,asymptotic_difference=abs(value-leading),
        source='https://arxiv.org/abs/1403.2309',source_equation='35 and64, neutral scalar, equal fermion masses',
        scope='CALIBRATED_LOCAL_RADIAL_HIGGS_LOOP_ONLY',native_evaluated=False,
        full_scalar_matching_and_interacting_LSZ_evaluated=False)
