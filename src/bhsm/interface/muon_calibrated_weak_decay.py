"""Calibrated Fermi decay rematching and non-Higgs weak current contributions.

Primary sector kernels/integrals are consumed separately. Fixed-Y Higgs terms,
native BHSM response and overlaps are never silently assigned SM or zero values.
"""
from __future__ import annotations
import math
from functools import lru_cache
import mpmath as mp
from scipy.integrate import quad
from scipy.special import spence
from .muon_calibrated_higher_qed import _positive, WEAK_PRIMARY

DECAY_PRIMARY = 'https://arxiv.org/abs/hep-ph/9904240'
DECAY_MASS_PRIMARY = 'https://arxiv.org/abs/0803.0960'
DECAY_VP_PRIMARY = 'https://arxiv.org/abs/hep-ph/9802341'
WEAK_CURRENT_PRIMARY = 'https://arxiv.org/abs/2503.04883'
DECAY_UPDATE_PRIMARY = 'https://arxiv.org/abs/2607.02657'
CHARGE_MATCHING_PRIMARY = 'https://arxiv.org/abs/1207.2199'


def muon_decay_phase_space(electron_muon_ratio):
    """Exact massless-neutrino three-body phase space, Eq.2.7."""
    _positive(rho=electron_muon_ratio)
    rho=float(electron_muon_ratio)
    if rho>=1:raise ValueError('electron mass must be below muon mass')
    x=rho*rho
    return 1-8*x-12*x*x*math.log(x)+8*x**3-x**4


@lru_cache(maxsize=64)
def muon_decay_one_loop_coefficient(electron_muon_ratio):
    """Integrate the complete finite-mass spectrum, van Ritbergen/Stuart C.3.

    The coefficient multiplies alpha_r/pi in the additive rate, not the
    phase-space factor. Real radiation and the virtual correction are already
    combined in this infrared-finite spectrum.
    """
    _positive(rho=electron_muon_ratio)
    rho=float(electron_muon_ratio)
    if not 0<rho<.02:raise ValueError('finite-mass integration is scoped to the muon/electron hierarchy')
    x=rho*rho
    def spectrum(z):
        z2=z*z;d=z2-x
        p0=2*x*x-3*x*(1+x)*z+8*x*z2-3*(1+x)*z**3+2*z**4
        a=-2*d*d/(3*z**5)*(5*x*x-10*x*(1+x)*z+(11+8*x+11*x*x)*z2-10*(1+x)*z**3+5*z**4)
        b=-d*d/(2*z**5)*(4*x*x-3*x*(1+3*x)*z+16*x*z2-3*(1+3*x)*z**3+4*z**4)*math.log(x)
        c=d/(6*z**5)*(4*x**3-3*x*x*(5-3*x)*z+12*x*(1+4*x-2*x*x)*z2
            +(5-87*x+9*x*x+5*x**3)*z**3+12*(1+4*x-2*x*x)*z**4-3*(5-3*x)*z**5+4*z**6)*math.log(z2/x)
        braces=(1-z)*(z+x)/(z2+x)*math.log1p(-x/z)
        braces-=(1+z)*(z-x)/(z2+x)*math.log1p(-z)
        braces+=math.log((1-z)/z)*math.log(z/x)+math.log(z)*math.log((z-x)/z2)
        braces+=-2*spence(x/z2)+2*spence(x/z)-2*spence(z)
        return a+b+c-2*(z**4-x*x)/z**5*p0*braces
    value,error=quad(spectrum,rho,1,points=[.02,.2,.8],epsabs=2e-11,epsrel=2e-11,limit=300)
    series=25/8-math.pi**2/2-(34+12*math.log(x))*x+16*math.pi**2*rho**3
    return dict(coefficient=value,quadrature_error_estimate=error,
        leading_mass_expansion=series,exact_minus_expansion=value-series,
        source=DECAY_PRIMARY,equation='Appendix C, C.1-C.3 integrated from sqrt(x) to 1')


def muon_decay_two_loop_finite_mass(electron_muon_ratio):
    """Pak/Czarnecki XA+XC+XH correction; no massless constant counted twice.

    QED color factors are CF=TR=1, CA=NL=0. Table I coefficients are retained
    through rho^7; the nonanalytic linear term is exact. Decimal table entries
    and a successive-term estimate have their own numerical scope.
    """
    _positive(rho=electron_muon_ratio)
    r=float(electron_muon_ratio)
    if r>=.02:raise ValueError('finite-mass series is scoped to the muon/electron hierarchy')
    l=math.log(r)
    rows={1:-5*math.pi**2*r/4,
        2:r*r*((-145.23+100.97-.30328)+(-105+52/3)*l-44*l*l),
        3:r**3*((-332.91+155.99)+210.55*l),
        4:r**4*((1807+112.72-8.8409)+(-130.61+343.28-8.2856)*l+(138.48+44)*l*l-176*l**3),
        5:r**5*((-617.86-188.62)+(1579.1+164.49)*l),
        6:r**6*((-610.71-235.84+7.5624)+(91.319+87.674-12.813)*l+(95.033-7.111+3.2)*l*l),
        7:r**7*((-39.188+144.75)+(301.79+177.65)*l)}
    return dict(coefficient_correction=math.fsum(rows.values()),powers={str(k):v for k,v in rows.items()},
        table_rounding_allowance=.02*r*r*(1+abs(l)*r+abs(l)**3*r*r),
        omitted_mass_power_estimate=2*abs(rows[7])*r,
        source=DECAY_MASS_PRIMARY,equations='Table I, CF=TR=1, CA=NL=0; finite XA+XC+XH only',
        rigorous_remainder_enclosure=None)


def _decay_vp_kernel(u):
    """Two-loop inclusive lifetime dispersion kernel, Eq.11/12 at 75 digits."""
    with mp.workdps(75):
        u=mp.mpf(str(u));d=1-u
        if d<mp.mpf('1e-9'):
            return float(mp.mpf(41)/300+(mp.mpf(85993)/7200-5*mp.zeta(2))*d/18
                +mp.log(d/2)/15*(1+mp.mpf(341)*d/144))
        u2=u*u;v=1-u2
        out=(1423+18979*u2-11699*u**4+513*u**6)/72
        out-=mp.mpf(2)/3*(85+127*u2-131*u**4+15*u**6)*mp.log(v/4)
        out-=(9-69*u2-37*u**4+33*u**6)/u*mp.log((1+u)/(1-u))
        out-=2*(19+180*u2-30*u**4-44*u**6+3*u**8)/v*(mp.pi**2/6+mp.log((1-u)/2)*mp.log((1+u)/2))
        out+=64*u*(3+4*u2-3*u**4)/v*(mp.polylog(2,(1+u)/2)-mp.polylog(2,(1-u)/2))
        return float(u*out/(9*v**4))


@lru_cache(maxsize=64)
def muon_decay_tau_vp(muon_tau_ratio):
    """Execute the tau bubble dispersion integral at the supplied pole masses."""
    _positive(r_tau=muon_tau_ratio)
    r=float(muon_tau_ratio)
    if r>=.2:raise ValueError('tau lifetime integral is scoped to m_mu/m_tau < 0.2')
    def fun(y):
        if y==0 or y==1:return 0.
        u=math.sqrt(1-r*r*y)
        return (1+y/2)*math.sqrt(1-y)*_decay_vp_kernel(u)*r*r/(2*u)
    value,error=quad(fun,0,1,epsabs=2e-12,epsrel=2e-9,limit=160)
    return dict(coefficient=value,quadrature_error_estimate=error,
        endpoint_series_threshold=1e-9,endpoint_series_truncation_estimate=1e-18,
        source=DECAY_VP_PRIMARY,equations='10-12, R_tau(s)=(1+2m_tau²/s)sqrt(1-4m_tau²/s)',
        muon_bubble_added=False)


def muon_lifetime_qed_factor(*,alpha_0,muon_electron_ratio,muon_tau_ratio):
    """Known QED lifetime correction through alpha³, with explicit estimates.

    The older alpha_e(m_mu) Eq.4.13 result is retained as a two-loop diagnostic.
    The third-order application restores the finite 15/16 OS/MS charge term.
    The strict Thomson-alpha expansion is also reported. Neutrino
    masses and electroweak matching are separate; GF is the Fermi-theory decay
    constant and no W-propagator factor is inserted into this definition.
    """
    _positive(alpha=alpha_0,r_e=muon_electron_ratio,r_t=muon_tau_ratio)
    a=float(alpha_0);re=float(muon_electron_ratio);rt=float(muon_tau_ratio)
    if not .006<a<.009:raise ValueError('alpha outside declared perturbative muon-decay domain')
    l=2*math.log(re);den=1-a*l/(3*math.pi)
    if den<=0:raise ValueError('electron running-charge denominator must be positive')
    ae=a/den+a**3*l/(4*math.pi**2)
    phase=muon_decay_phase_space(1/re);one=muon_decay_one_loop_coefficient(1/re)
    mass=muon_decay_two_loop_finite_mass(1/re);tau=muon_decay_tau_vp(rt)
    with mp.workdps(45):
        c2=float(mp.mpf(156815)/5184-mp.mpf(1036)/27*mp.zeta(2)-mp.mpf(895)/36*mp.zeta(3)
            +mp.mpf(67)/8*mp.zeta(4)+53*mp.zeta(2)*mp.log(2))
    c2_total=c2+mass['coefficient_correction']-.042+tau['coefficient']
    q1=ae/math.pi*one['coefficient'];q2=(ae/math.pi)**2*c2_total
    two_loop_factor=phase+q1+q2
    strict=phase+a/math.pi*one['coefficient']+(a/math.pi)**2*(c2_total+l/3*one['coefficient'])
    # The current primary update evaluates the order-three coefficient with
    # electron MSbar charge. At this finite order the required OS->MS relation
    # is exactly C1=L/3, C2=L²/9+L/4+15/16 (1207.2199 Eq34-35, N=1).
    # Heavy bubbles remain explicitly in the decay coefficients, rather than
    # adding a second heavy-threshold conversion to this convention.
    t=a/math.pi;a1=l/3;a2=l*l/9+l/4+15/16
    abar=a*(1+a1*t+a2*t*t)
    c3_parts=dict(muon_loop=2.109799281,muon_loop_squared=-.01876788909,
        electron_loop=-7.187551125,electron_loop_squared=-6.919459635,
        mixed_muon_electron=-.01288114148,photonic_extrapolation=-6.2)
    c3=math.fsum(c3_parts.values())
    current_hadron=-.0428
    c2_current=c2+mass['coefficient_correction']+current_hadron+tau['coefficient']
    q1_current=abar/math.pi*one['coefficient'];q2_current=(abar/math.pi)**2*c2_current
    q3=(abar/math.pi)**3*c3
    # Eq16 is explicitly an estimate, not a completed hadronic integration.
    # Its amplitude scales as GF^0*(alpha_bar/pi)^3 in Delta_q.
    abar_ref=1/135.901928274
    had3_scale=(abar/abar_ref)**3
    had3_estimate=27e-9*had3_scale
    factor=phase+q1_current+q2_current+q3+had3_estimate
    strict3=phase+one['coefficient']*t+(c2_current+a1*one['coefficient'])*t*t
    strict3+=(c3+2*a1*c2_current+a2*one['coefficient'])*t**3+had3_estimate
    return dict(rate_factor=factor,two_loop_rate_factor=two_loop_factor,
        strict_alpha_0_order2_rate_factor=strict,strict_alpha_0_order3_rate_factor=strict3,
        delta_q0=phase-1,delta_q1=q1_current,delta_q2=q2_current,delta_q3=q3,
        two_loop_diagnostic_delta_q1=q1,two_loop_diagnostic_delta_q2=q2,
        current_delta_q1=q1_current,current_delta_q2=q2_current,current_delta_q3=q3,
        current_hadronic_delta_q3_estimate=had3_estimate,
        alpha_e_mu=ae,alpha_e_mu_inverse=1/ae,
        alpha_MSbar_known_order3=abar,alpha_MSbar_known_order3_inverse=1/abar,
        charge_conversion=dict(source=CHARGE_MATCHING_PRIMARY,equations='34-35, N=1, mu=m_mu, M=m_e',
            coefficients=[a1,a2],complete_alpha0_to_MSbar_four_loop_conversion_used=False,
            retained_accuracy='OS/MS relation through alpha0^3, sufficient for strict decay through alpha0^3'),
        third_order=dict(coefficient=c3,components=c3_parts,coefficient_standard_uncertainty=1.6,
            source=DECAY_UPDATE_PRIMARY,equation='10, nl=nh=1; photonic part extrapolated with uncertainty'),
        massless_two_loop_coefficient=c2,two_loop_coefficient_with_mass_hadron_tau=c2_total,
        current_two_loop_coefficient_with_mass_hadron_tau=c2_current,
        one_loop=one,finite_electron_two_loop=mass,tau_vp=tau,
        hadronic_vp=dict(coefficient=-.042,standard_uncertainty=.002,
            source=DECAY_VP_PRIMARY,equation='16',mass_reference_use='published dispersion integral at physical muon mass; nearby-mass use'),
        current_hadronic_vp=dict(coefficient=current_hadron,standard_uncertainty=.0006,
            source=DECAY_UPDATE_PRIMARY,equations='12-15',
            input_scope='unweighted KNT19 and KNT19/CMD3 mean; half spread retained; no measured a_mu input'),
        hadronic_third_order_estimate=dict(value=had3_estimate,standard_uncertainty=abs(had3_estimate),
            source=DECAY_UPDATE_PRIMARY,equation='16',status='ESTIMATE_NOT_COMPLETED_INTEGRAL'),
        errors=dict(one_loop_quadrature_estimate=abar/math.pi*one['quadrature_error_estimate'],
            two_loop_table_rounding_allowance=(abar/math.pi)**2*mass['table_rounding_allowance'],
            two_loop_mass_power_truncation_estimate=(abar/math.pi)**2*mass['omitted_mass_power_estimate'],
            hadronic_vp_standard_uncertainty=(abar/math.pi)**2*.0006,
            hadronic_nearby_masspoint_allowance=(abar/math.pi)**2*abs(current_hadron)*2e-6,
            tau_quadrature_estimate=(abar/math.pi)**2*tau['quadrature_error_estimate'],
            resummed_minus_strict_order2=two_loop_factor-strict,
            reorganized_minus_strict_order3=factor-strict3,
            photonic_alpha3_coefficient_standard_uncertainty=(abar/math.pi)**3*1.6,
            hadronic_alpha3_estimated_standard_uncertainty=abs(had3_estimate),
            alpha3_finite_electron_estimate=(abar/math.pi)**3*abs(math.log(1/re))/re,
            omitted_order_rate_allowance_estimate=max(1e-8,2*abs(factor-strict3)),
            omitted_order_scope='conservative perturbative estimate, not an enclosure'),
        source=DECAY_UPDATE_PRIMARY,equations='2,6,9,10,15-16; exact one-loop spectrum from 9904240 Appendix C',
        convention='additive phase+Delta_q1+Delta_q2+Delta_q3; on-shell pole masses; Thomson alpha input; electron-MSbar conversion through needed order',
        W_propagator_correction_in_GF_definition=False,complete_decay_error=False)


def rematch_fermi_constant(*,alpha_0,muon_electron_ratio,muon_tau_ratio,
                          muon_mass_GeV,lifetime_seconds,hbar_GeV_seconds):
    """Extract GF from the measured inclusive muon lifetime, without a_mu input."""
    _positive(m=muon_mass_GeV,tau=lifetime_seconds,hbar=hbar_GeV_seconds)
    factor=muon_lifetime_qed_factor(alpha_0=alpha_0,muon_electron_ratio=muon_electron_ratio,muon_tau_ratio=muon_tau_ratio)
    m=float(muon_mass_GeV);t=float(lifetime_seconds);hb=float(hbar_GeV_seconds)
    gf=math.sqrt(192*math.pi**3*hb/(t*m**5*factor['rate_factor']))
    reproduced=192*math.pi**3*hb/(gf*gf*m**5*factor['rate_factor'])
    error=factor['errors']
    rate_std=math.sqrt(error['hadronic_vp_standard_uncertainty']**2
        +error['photonic_alpha3_coefficient_standard_uncertainty']**2
        +error['hadronic_alpha3_estimated_standard_uncertainty']**2)
    return dict(G_F_GeV_minus2=gf,lifetime_factor=factor,reconstructed_lifetime_seconds=reproduced,
        relative_lifetime_residual=reproduced/t-1,
        fixed_ratio_derivatives=dict(muon_mass=-2.5*gf/m,lifetime_seconds=-gf/(2*t)),
        hadronic_vp_GF_standard_uncertainty=gf*.5*factor['errors']['hadronic_vp_standard_uncertainty']/factor['rate_factor'],
        decay_rate_combined_estimated_standard_uncertainty=rate_std,
        decay_GF_combined_estimated_standard_uncertainty=gf*.5*rate_std/factor['rate_factor'],
        decay_uncertainty_scope='quadrature combination of source numerical QED uncertainty and estimated hadronic alpha3 uncertainty; no complete error claim',
        omitted_order_GF_allowance_estimate=gf*.5*factor['errors']['omitted_order_rate_allowance_estimate']/factor['rate_factor'],
        measured_anomaly_used=False,full_electroweak_matching_evaluated=False,
        classification='CALIBRATED_FERMI_DECAY_CONSTANT_KNOWN_QED_ORDERS_WITH_EXPLICIT_TRUNCATION')


def muon_lifetime_rate_log_derivatives(*,alpha_0,muon_electron_ratio,muon_tau_ratio):
    """Differentiate the executed rate factor in its three independent inputs.

    Pole mass and lifetime powers are not included here; consumers must chain
    these through their measured primitive masses, including shared alpha/R/r.
    """
    inputs=dict(alpha_0=alpha_0,muon_electron_ratio=muon_electron_ratio,muon_tau_ratio=muon_tau_ratio)
    h=1e-4;out={}
    for key,value in inputs.items():
        plus=dict(inputs);minus=dict(inputs)
        plus[key]=value*math.exp(h);minus[key]=value*math.exp(-h)
        out[key]=(muon_lifetime_qed_factor(**plus)['rate_factor']-muon_lifetime_qed_factor(**minus)['rate_factor'])/(2*h)
    return dict(derivative_log_inputs=out,central_log_step=h,
        scope='finite differences of the literal selected finite-order expression, not a covariance or theory-error derivative')


def electroweak_two_loop_fermionic_rest(*,alpha_0,fermi_constant_GeV_inverse_squared,
        muon_mass_GeV,tau_mass_GeV,w_mass_GeV,z_mass_GeV,top_pole_mass_GeV,
        gamma_z_correlator=6.0,gamma_z_correlator_standard_uncertainty=.1):
    """Execute the three non-Higgs remainder terms, Eq.20 with updated Eq.23.

    The top pole mass enters gauge self-energies, not a fitted Higgs Yukawa.
    The correlator value is a separately evaluated primary QCD/current input.
    The source approximation omits higher powers of 1-4sW² and MZ²/mt².
    """
    _positive(alpha=alpha_0,GF=fermi_constant_GeV_inverse_squared,m=muon_mass_GeV,
        tau=tau_mass_GeV,MW=w_mass_GeV,MZ=z_mass_GeV,mt=top_pole_mass_GeV,
        gammaZ=gamma_z_correlator,uncertainty=gamma_z_correlator_standard_uncertainty)
    sw=1-(w_mass_GeV/z_mass_GeV)**2
    if not 0<sw<1:raise ValueError('on-shell weak mixing angle must lie strictly between zero and one')
    pref=fermi_constant_GeV_inverse_squared*muon_mass_GeV**2*alpha_0/(8*math.sqrt(2)*math.pi**3)
    v=1-4*sw;r=(top_pole_mass_GeV/w_mass_GeV)**2
    coefficients=dict(top_W_gauge_remainder=(5*r/8+math.log(r)+7/3)/(2*sw),
        delta_rho_weak_angle=(1-sw)*r*v/(2*sw),
        lepton_gamma_Z_log=(8*math.log(z_mass_GeV/muon_mass_GeV)/9+4*math.log(z_mass_GeV/tau_mass_GeV)/9)*v*v,
        hadronic_gamma_Z_mixing=4*gamma_z_correlator*v/3)
    rows={k:-pref*c for k,c in coefficients.items()}
    return dict(a_mu_fermionic_rest_no_H=math.fsum(rows.values()),contributions=rows,
        dimensionless_coefficients=coefficients,common_prefactor=pref,sin_squared_theta_W=sw,
        gamma_Z_current_correlator=dict(value=gamma_z_correlator,standard_uncertainty=gamma_z_correlator_standard_uncertainty,
            source=WEAK_CURRENT_PRIMARY,equations='23-26; 8pi² Pi_bar_gammaZ(-MZ²)=6.0(1)'),
        gamma_Z_correlator_induced_standard_uncertainty=abs(pref*4*v/3)*gamma_z_correlator_standard_uncertainty,
        source_expansion_uncertainty_allowance=1e-12,
        source_expansion_uncertainty_scope='2025 Table I rest error 0.10e-11, including omitted weak-angle/heavy-top terms; not rigorous',
        source=WEAK_PRIMARY,equation='20',top_Yukawa_fitted=False,Higgs_diagrams_included=False,
        whole_EW_evaluated=False,native_evaluated=False)


def _vva_mass_factor_difference(q_squared,mass_selected,mass_reference):
    """Difference of Q² integral x(1-x)/(Q²x(1-x)+m²), Eq.3."""
    def small(k):
        term=k/6;out=[]
        for n in range(1,31):
            out.append(term);term*=-k*(n+1)**2/((2*n+3)*(2*n+2))
        return math.fsum(out)
    ks=q_squared/mass_selected**2;kr=q_squared/mass_reference**2
    if max(ks,kr)<.05:return small(ks)-small(kr)
    def deficit(k):return 4*math.asinh(math.sqrt(k)/2)/(k*math.sqrt(1+4/k))
    # Subtract deficits rather than two values close to one at large Q².
    return deficit(kr)-deficit(ks)


def _vva_kinematic_weights(q_squared,muon_mass,z_mass):
    z=q_squared/muon_mass**2;W=math.sqrt(1+4/z);d=4/(z*(W+1))
    return d*(W+2)/(W+1),d*(2*W+1)/(W+1)*z_mass**2/(z_mass**2+q_squared)


def vva_perturbative_masspoint_shift(*,alpha_0,fermi_constant_GeV_inverse_squared,
        muon_mass_GeV,z_mass_GeV,fermion_mass_GeV,reference_fermion_mass_GeV,
        electric_charge,weak_isospin,color_factor):
    """Execute the Eq.1-3 one-loop VVA mass difference, not a new whole sector.

    The difference is UV convergent; the physical sector itself must include
    all three anomaly-cancelling generation members. Source alpha_s and
    nonperturbative corrections are not recomputed by this mass shift.
    """
    _positive(alpha=alpha_0,GF=fermi_constant_GeV_inverse_squared,m=muon_mass_GeV,MZ=z_mass_GeV,
        mf=fermion_mass_GeV,mref=reference_fermion_mass_GeV)
    if color_factor not in (1,3) or weak_isospin not in (-.5,.5) or not math.isfinite(electric_charge):
        raise ValueError('finite physical charge/isospin and color1 or3 required')
    if abs(math.log(fermion_mass_GeV/reference_fermion_mass_GeV))>.03:
        raise ValueError('VVA mass difference outside declared nearby-reference domain')
    pref=alpha_0*fermi_constant_GeV_inverse_squared/(24*math.sqrt(2)*math.pi**3)
    weight=4*weak_isospin*color_factor*electric_charge**2
    def fun(y):
        q2=math.exp(y);cL,cT=_vva_kinematic_weights(q2,muon_mass_GeV,z_mass_GeV)
        # Both Q² terms in cT have denominator 2*m_mu² (PDF Eq2).
        # Rationalization exposes cL,cT~3*m_mu²/Q², preventing cancellation
        # loss and an erroneous unsuppressed GF*MZ² contribution.
        return weight*q2*(cL+cT/2)*_vva_mass_factor_difference(q2,fermion_mass_GeV,reference_fermion_mass_GeV)
    value,error=quad(fun,-40,50,epsabs=2e-10,epsrel=2e-8,limit=200,
        points=[math.log(fermion_mass_GeV**2),math.log(z_mass_GeV**2)])
    return dict(a_mu_shift=pref*value,quadrature_error_estimate=abs(pref)*error,
        reference_mass_GeV=reference_fermion_mass_GeV,selected_mass_GeV=fermion_mass_GeV,
        log_Q_squared_interval=[-40,50],source=WEAK_CURRENT_PRIMARY,equations='1-3, wT=wL/2',
        uncomputed_mass_dependence='alpha_s/nonperturbative corrections and finite tail retained in separate approximation allowance',
        separately_physical_generation_sector=False)


def electroweak_two_loop_vva_sectors(*,alpha_0,fermi_constant_GeV_inverse_squared,muon_mass_GeV,
                                    top_pole_mass_GeV=None,tau_mass_GeV=None,z_mass_GeV=91.1876):
    """Consume primary VVA sector integrals; no full EW total is imported.

    Near-reference GF*m_mu²*alpha scaling is exact for the common prefactor.
    Internal mass shapes/current kernels are the published 2025 ones; this use
    is an approximation, with a separate allowance rather than fictitious mass
    derivatives. These three-generation current sectors are anomaly-cancelled
    combinations, not separately selected quark Higgs couplings.
    """
    _positive(alpha=alpha_0,GF=fermi_constant_GeV_inverse_squared,m=muon_mass_GeV)
    ref=dict(alpha_inverse=137.035999,GF_GeV_minus2=1.1663787e-5,muon_mass_GeV=.1056583755)
    scale=(alpha_0*ref['alpha_inverse'])*(fermi_constant_GeV_inverse_squared/ref['GF_GeV_minus2'])*(muon_mass_GeV/ref['muon_mass_GeV'])**2
    if abs(scale-1)>.001:raise ValueError('VVA sector use outside nearby-reference prefactor domain')
    rows=[dict(generation=n,a_mu=v*1e-11*scale,source_standard_uncertainty=u*1e-11*scale)
        for n,v,u in (('u,d,e',-2.08,.03),('c,s,mu',-4.14,.28),('t,b,tau',-8.12,.01))]
    shifts=[]
    if (top_pole_mass_GeV is None)!=(tau_mass_GeV is None):raise ValueError('top and tau masspoint inputs must be supplied together')
    if top_pole_mass_GeV is not None:
        for name,mass,reference,charge,isospin,color in (('top',top_pole_mass_GeV,172.57,2/3,.5,3),
                ('tau',tau_mass_GeV,1.77686,-1,-.5,1)):
            shift=vva_perturbative_masspoint_shift(alpha_0=alpha_0,fermi_constant_GeV_inverse_squared=fermi_constant_GeV_inverse_squared,
                muon_mass_GeV=muon_mass_GeV,z_mass_GeV=z_mass_GeV,fermion_mass_GeV=mass,
                reference_fermion_mass_GeV=reference,electric_charge=charge,weak_isospin=isospin,color_factor=color)
            shifts.append(dict(fermion=name,**shift))
        rows[2]['published_reference_prefactor_rescaled_value']=rows[2]['a_mu']
        rows[2]['a_mu']+=math.fsum(row['a_mu_shift'] for row in shifts)
    return dict(a_mu_VVA=math.fsum(row['a_mu'] for row in rows),contributions=rows,
        reference_prefactor_inputs=ref,prefactor_rescaling=scale,
        reference_internal_masses_GeV=dict(top_source_MC_parameter=172.57,tau=1.77686,
            bottom_MSbar=4.183,charm_MSbar=1.2730),
        internal_mass_source_scope='2503.04883 footnote1, mb/mc converted to OS through alpha_s; source alpha_s variation also covers its reference Monte Carlo top-to-pole correction',
        third_generation_perturbative_masspoint_shifts=shifts,
        source_standard_uncertainty_quadrature_if_uncorrelated=math.sqrt(sum(row['source_standard_uncertainty']**2 for row in rows)),
        source_standard_uncertainty_sum_over_all_correlations=sum(row['source_standard_uncertainty'] for row in rows),
        published_sector_covariance=None,mass_shape_approximation_allowance=1e-13,
        mass_shape_approximation_scope='0.07% of VVA magnitude estimate covers uncomputed kernel, alpha_s-mass/tail changes; top/tau one-loop mass difference executed, not a bound or full derivative',
        source=WEAK_CURRENT_PRIMARY,equations='4,6,22,Table I; first/second generation primary dispersive kernels',
        selected_Higgs_Yukawa=False,whole_EW_total_imported=False,
        native_evaluated=False,whole_EW_evaluated=False)
