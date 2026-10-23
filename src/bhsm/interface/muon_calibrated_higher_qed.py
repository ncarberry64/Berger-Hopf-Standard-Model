"""Calibrated local QED orders three through five, with explicit approximations.

Only leptonic on-shell QED is included. Published numerical integrations at
their stated reference masses are coefficients, not measured anomaly inputs.
Neither native BHSM response nor its overlap is evaluated or set to zero.
"""
from __future__ import annotations

import math
import mpmath as mp
from scipy.integrate import quad

QED_PRIMARY = 'https://arxiv.org/abs/1205.5370'
QED_LEDGER = 'https://arxiv.org/abs/2006.04822'
UNIVERSAL_FIVE_LOOP = [
    'https://arxiv.org/abs/2404.00649',
    'https://arxiv.org/abs/2412.06473',
]
QED_UPDATE = 'https://arxiv.org/abs/2505.21476'
WEAK_PRIMARY = 'https://arxiv.org/abs/1306.5546'
ELECTRON_RATIO_REFERENCE = 206.7682843
TAU_RATIO_REFERENCE = .0594649


def _positive(**values):
    for name, value in values.items():
        if not math.isfinite(float(value)) or float(value) <= 0:
            raise ValueError(f'{name} must be positive and finite')


def universal_three_loop_coefficient():
    """Laporta--Remiddi exact constant (WP20 Eq.6.6), evaluated at 50 digits."""
    with mp.workdps(50):
        p, l, z = mp.pi, mp.log(2), mp.zeta
        return float(mp.mpf(83)/72*p*p*z(3)-mp.mpf(215)/24*z(5)
            +mp.mpf(100)/3*mp.polylog(4,mp.mpf('.5'))+mp.mpf(25)/18*l**4
            -mp.mpf(25)/18*p*p*l*l-mp.mpf(239)/2160*p**4
            +mp.mpf(139)/18*z(3)-mp.mpf(298)/9*p*p*l
            +mp.mpf(17101)/810*p*p+mp.mpf(28259)/5184)


def _electron_three_loop_series(ratio, order=2):
    # WP20 Eq.6.15, used only for a nearby mass-point DIFFERENCE.
    x=1/float(ratio); l=math.log(x); p=math.pi; z3=float(mp.zeta(3))
    a4=float(mp.polylog(4,.5)); l2=math.log(2)
    out=2*l*l/9-(z3-2*p*p*l2/3+7*p*p/9+31/27)*l
    out+=97*p**4/360-2*p*p*l2*l2/9-8*a4/3-l2**4/9-6*z3+5*p*p*l2/3-85*p*p/18+1219/216
    if order>=1:
        out+=x*(-4*p*p*l/3-604*p*p*l2/9+54079*p*p/1080-13*p**3/18)
    if order>=2:
        out+=x*x*(2*l**3/3+(p*p/9-10/3)*l*l
            +(16*p**4/135+4*z3-32*p*p/9+194/9)*l
            +4*z3*p*p/3-61*p**4/270+z3+197*p*p/36-2809/108-14*p*p*l2/3)
    return out


def _tau_three_loop_series(ratio, order=4):
    # WP20 Eq.6.16; ratio is m_mu/m_tau, not its reciprocal.
    r=float(ratio); l=-math.log(r); p=math.pi; z3=float(mp.zeta(3))
    out=r*r*(-23*l/135-74957/97200-2*p*p/45+1.5*z3)
    if order>=4:
        out+=r**4*(-4337*l*l/22680-209891*l/476280
            -451205689/533433600-1919*p*p/68040+1811*z3/2304)
    return out


def _vp(k, derivative=False):
    """Pi(-Q²)/(alpha/pi), Pi(0)=0; stable exact elementary representation."""
    if k<1:
        term=k/15; out=[]
        for n in range(1,41):
            out.append(2*n*term if derivative else term)
            term*=-k*n*(n+2)**2/((n+1)*(2*n+5)*(2*n+4))
        return math.fsum(out)
    v=math.sqrt(1+4/k); l=2*math.asinh(math.sqrt(k)/2)
    if derivative:return 2/3-4/k+8*l/(k*k*v)
    return 4/(3*k)-5/9+(1-2/k)*v*l/3


def mixed_three_loop_vp(muon_electron_ratio,muon_tau_ratio,*,eps=2e-12):
    """Execute the two differently massive VP insertions, including factor two.

    A3^(6)=2 int_0^1 (1-x) Pi_e(-Q²) Pi_tau(-Q²) dx,
    Q²/m_mu²=x²/(1-x). Both bubbles have the Thomson subtraction.
    The common-photon permutations are counted exactly once by factor two.
    """
    _positive(r_e=muon_electron_ratio,r_t=muon_tau_ratio,eps=eps)
    re=float(muon_electron_ratio);rt=float(muon_tau_ratio)
    splits=[2/(1+math.sqrt(1+4*r*r)) for r in (re,rt)]
    def integrand(x,which=0):
        if x==1:return 0.
        k=x*x/(1-x); e=_vp(re*re*k,which==1); t=_vp(rt*rt*k,which==2)
        return 2*(1-x)*e*t
    options=dict(epsabs=eps,epsrel=eps,limit=300,points=splits)
    pairs=[quad(lambda x:integrand(x,i),0,1,**options) for i in range(3)]
    return dict(coefficient=pairs[0][0],quadrature_error_estimate=pairs[0][1],
        derivative_log_electron_ratio=pairs[1][0],derivative_log_tau_ratio=pairs[2][0],
        derivative_quadrature_error_estimates=[p[1] for p in pairs[1:]],
        source='https://arxiv.org/abs/hep-ph/9812394',equation='mixed two-VP diagram, Eq.10')


def calibrated_higher_qed(*,alpha,muon_electron_ratio,muon_tau_ratio):
    """Return new local terms ONLY; the existing alpha and alpha² terms stay out.

    C3 is moved to the selected mass point by analytic series differences;
    its two-mass coefficient is directly integrated. C4/C5 are the published
    reference-mass integrals. Their nearby mass-point use is an approximation,
    with a separate leading-log diagnostic and error allowance, never a bound.
    """
    _positive(alpha=alpha,r_e=muon_electron_ratio,r_t=muon_tau_ratio)
    a=float(alpha);re=float(muon_electron_ratio);rt=float(muon_tau_ratio)
    # Restrict approximation to its deliberately small reference neighbourhood.
    if abs(math.log(re/ELECTRON_RATIO_REFERENCE))>1e-4 or abs(math.log(rt/TAU_RATIO_REFERENCE))>1e-3:
        raise ValueError('mass point outside the declared nearby-reference approximation domain')
    ep=lambda order:_electron_three_loop_series(re,order)-_electron_three_loop_series(ELECTRON_RATIO_REFERENCE,order)
    tp=lambda order:_tau_three_loop_series(rt,order)-_tau_three_loop_series(TAU_RATIO_REFERENCE,order)
    mixed=mixed_three_loop_vp(re,rt)
    c3=universal_three_loop_coefficient()+22.86838004+ep(2)+.00036070+tp(4)+mixed['coefficient']
    c4=-1.912245764926445574+132.6852+.0424941+.062722
    c5=5.887+742.32-.0656+2.011
    x=a/math.pi
    terms={f'local_leptonic_QED_{n}_loop':c*x**n for n,c in ((3,c3),(4,c4),(5,c5))}
    # Finite-difference derivative of the explicit analytic mass-point correction,
    # not a derivative of a total anomaly or of the selected physical state.
    h=1e-4
    de=(_electron_three_loop_series(re*math.exp(h))-_electron_three_loop_series(re*math.exp(-h)))/(2*h)
    dt=(_tau_three_loop_series(rt*math.exp(h))-_tau_three_loop_series(rt*math.exp(-h)))/(2*h)
    # Dominant LL times VP logarithm gives a sensitivity DIAGNOSTIC, not the
    # full C4/C5 mass derivative. WP20 Eq.6.24 licenses this power counting.
    log_ref=math.log(ELECTRON_RATIO_REFERENCE);v=2*log_ref/3-5/9;ll=20.94792485
    d4=3*((2*math.pi**2/3)*v+ll*2/3)
    d5=6*((2*math.pi**2/3)*v*v+ll*2*v*2/3)
    c4_shift_est=d4*math.log(re/ELECTRON_RATIO_REFERENCE)+2*(.0424941+.062722)*math.log(rt/TAU_RATIO_REFERENCE)
    c5_shift_est=d5*math.log(re/ELECTRON_RATIO_REFERENCE)+2*(-.0656+2.011)*math.log(rt/TAU_RATIO_REFERENCE)
    c3_update_est=2*(abs(ep(2)-ep(1))+abs(tp(4)-tp(2)))*x**3
    c4c5_masspoint_allowance=max(1e-14,10*(abs(c4_shift_est)*x**4+abs(c5_shift_est)*x**5))
    return dict(classification='CALIBRATED_LOCAL_ON_SHELL_LEPTONIC_QED_THROUGH_ALPHA5_INCREMENT',
        inputs=dict(alpha=a,muon_electron_ratio=re,muon_tau_ratio=rt),
        reference_mass_point=dict(muon_electron_ratio=ELECTRON_RATIO_REFERENCE,muon_tau_ratio=TAU_RATIO_REFERENCE,
            role='published-integral reference only; not selected mass calibration'),
        coefficients=dict(C3=c3,C4=c4,C5=c5),contributions=terms,increment=math.fsum(terms.values()),
        mixed_three_loop=mixed,
        C3_masspoint_updates=dict(electron=ep(2),tau=tp(4),electron_order1=ep(1),tau_order2=tp(2)),
        derivative_alpha=math.fsum(n*c*x**n/a for n,c in ((3,c3),(4,c4),(5,c5))),
        derivative_log_muon_electron_ratio=(de+mixed['derivative_log_electron_ratio'])*x**3,
        derivative_log_muon_tau_ratio=(dt+mixed['derivative_log_tau_ratio'])*x**3,
        derivative_scope='C3 selected-mass derivative; C4/C5 reference-point mass derivatives estimated separately',
        errors=dict(published_C4_integration_standard_uncertainty=math.hypot(.0060,math.hypot(.0000053,.000010))*x**4,
            published_C5_integration_standard_uncertainty=math.sqrt(.055**2+.86**2+.0045**2+.010**2)*x**5,
            C3_anchor_rounding_and_reference_rounding_allowance=2e-8*x**3,
            C3_masspoint_update_truncation_estimate=c3_update_est,
            mixed_C3_quadrature_error_estimate=mixed['quadrature_error_estimate']*x**3,
            C4_C5_reference_masspoint_approximation_allowance=c4c5_masspoint_allowance,
            C4_leading_log_masspoint_shift_diagnostic=c4_shift_est*x**4,
            C5_leading_log_masspoint_shift_diagnostic=c5_shift_est*x**5,
            omitted_alpha6_estimated_standard_uncertainty=1e-12,
            all_orders_remainder_enclosure=None,
            approximation_scope='near-reference mass sensitivity and omitted-order estimates, not rigorous enclosures'),
        sources=dict(C3_anchor=dict(url=QED_PRIMARY,equations='9, with reference mass ratios'),
            C3_series=dict(url=QED_LEDGER,equations='6.15-6.17'),
            C4=dict(url=QED_LEDGER,equations='6.8,6.18-6.20'),
            C5_mass_dependent=dict(url=QED_LEDGER,equations='6.21-6.23'),
            C5_universal=dict(primary=UNIVERSAL_FIVE_LOOP,weighted_average_source=QED_UPDATE,equation='7.19'),
            alpha6_estimate=dict(url=QED_LEDGER,equations='6.24-6.25, Table18')),
        native_remainder=None,complete_observable=False,action_selected=False,Gate7_closed=False,
        measured_anomaly_used=False,old_two_loop_subtotal_included=False)


def leading_electroweak_pauli(*,fermi_constant_GeV_inverse_squared,muon_mass_GeV,
                             w_mass_GeV,z_mass_GeV):
    """Execute leading on-shell EW formula, Gnendiger et al. Eq.8.

    The tiny radial-Higgs one-loop diagram is omitted here and remains in
    the preserved fixed-Y subtotal. This is not the complete two-loop EW sum.
    """
    _positive(GF=fermi_constant_GeV_inverse_squared,m=muon_mass_GeV,MW=w_mass_GeV,MZ=z_mass_GeV)
    sw=1-(w_mass_GeV/z_mass_GeV)**2
    if not 0<sw<1:raise ValueError('on-shell weak mixing angle must lie strictly between zero and one')
    c=5/3+(1-4*sw)**2/3
    value=fermi_constant_GeV_inverse_squared*muon_mass_GeV**2*c/(8*math.sqrt(2)*math.pi**2)
    ds=-8*(1-4*sw)/3
    return dict(a_mu_leading_EW=value,sin_squared_theta_W=sw,
        derivatives=dict(GF=value/fermi_constant_GeV_inverse_squared,muon_mass=2*value/muon_mass_GeV,
            w_mass=value*ds/c*(-2*w_mass_GeV/z_mass_GeV**2),
            z_mass=value*ds/c*(2*w_mass_GeV**2/z_mass_GeV**3)),
        source=WEAK_PRIMARY,equation='8',radial_Higgs_one_loop_included=False,
        omitted_terms='terms suppressed by m_mu²/M_Z² or m_mu²/M_H²; higher EW orders',
        full_EW_evaluated=False,native_evaluated=False)


def _log_over_difference(u,x):
    d=(u-x)/x
    return -1/x if abs(d)<1e-10 else -math.log1p(d)/(u-x)


def higgs_photon_barr_zee_kernel(x):
    """Gnendiger Eq.14 with removable denominator evaluated continuously."""
    _positive(x=x)
    def fun(w):
        u=w*(1-w)
        return x*(1-2*u)*_log_over_difference(u,x)
    v,e=quad(fun,0,1,epsabs=1e-10,epsrel=2e-11,limit=250)
    return dict(value=v,quadrature_error_estimate=e,source=WEAK_PRIMARY,equation='14')


def higgs_z_barr_zee_kernel(x,z):
    """Gnendiger Eq.17, including its continuous equal-mass limit."""
    _positive(x=x,z=z)
    def fun(w):
        u=w*(1-w)
        if abs(x-z)<=1e-8*max(x,z):
            mid=(x+z)/2;d=(u-mid)/mid
            dg=(.5-d/3+d*d/4)/(mid*mid) if abs(d)<1e-5 else (d-math.log1p(d))/(u-mid)**2
            return -mid*mid*(1-2*u)*dg
        return x*z*(1-2*u)*(_log_over_difference(u,z)-_log_over_difference(u,x))/(x-z)
    value,error=quad(fun,0,1,epsabs=1e-10,epsrel=2e-11,limit=250)
    return dict(value=value,quadrature_error_estimate=error,source=WEAK_PRIMARY,equation='17')


def fixed_yukawa_lepton_barr_zee_photon(*,alpha,muon_mass_GeV,higgs_mass_GeV,lepton_masses_GeV):
    """Evaluate the charged-lepton Hγ subdiagrams using the existing fixed Y_l.

    Internal order is (tau,muon,electron). No top/quark Yukawa is invented.
    This is separate from scalar one-loop and from imported EW bosonic pieces.
    """
    from .ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
    _positive(alpha=alpha,muon_mass=muon_mass_GeV,higgs_mass=higgs_mass_GeV)
    masses=list(lepton_masses_GeV)
    if len(masses)!=3:raise ValueError('three masses in tau,muon,electron order required')
    for m in masses:_positive(lepton_mass=m)
    y=charged_lepton_yukawa_operator()['eigenvalues_heavy_middle_light']
    g=[float(v)/math.sqrt(2) for v in y]
    rows=[]
    for name,m,gf in zip(('tau','muon','electron'),masses,g):
        k=higgs_photon_barr_zee_kernel((m/higgs_mass_GeV)**2)
        pref=alpha*muon_mass_GeV*g[1]*gf/(8*math.pi**3*m)
        rows.append(dict(internal_lepton=name,a_mu=pref*k['value'],higgs_coupling=gf,
            quadrature_error_estimate=abs(pref)*k['quadrature_error_estimate'],kernel=k))
    return dict(contributions=rows,a_mu_Hgamma_charged_leptons=math.fsum(r['a_mu'] for r in rows),
        equation='1306.5546 Eq12 with m_mu*m_f/v² replaced by g_hmu*g_hf',
        fixed_Y_owner='ae31_c2_intrinsic_m4_lepton_action.charged_lepton_yukawa_operator',
        included='charged-lepton Hγ only',quark_Hgamma_included=False,HZ_included=False,
        whole_EW_evaluated=False,source=WEAK_PRIMARY,action_selected=False)


def fixed_yukawa_lepton_barr_zee_z(*,alpha,muon_mass_GeV,higgs_mass_GeV,
                                  lepton_masses_GeV,w_mass_GeV,z_mass_GeV):
    """Charged-lepton HZ partner of the same literal fixed-Y diagrams."""
    from .ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
    _positive(alpha=alpha,m=muon_mass_GeV,MH=higgs_mass_GeV,MW=w_mass_GeV,MZ=z_mass_GeV)
    sw=1-(w_mass_GeV/z_mass_GeV)**2
    if not 0<sw<1:raise ValueError('on-shell weak mixing angle must lie strictly between zero and one')
    masses=list(lepton_masses_GeV)
    if len(masses)!=3:raise ValueError('three masses in tau,muon,electron order required')
    g=[float(y)/math.sqrt(2) for y in charged_lepton_yukawa_operator()['eigenvalues_heavy_middle_light']]
    rows=[]
    charge=-1;isospin=-.5
    weak=charge*(isospin-2*sw*charge)*(1-4*sw)/(4*(1-sw)*sw)
    for name,m,gf in zip(('tau','muon','electron'),masses,g):
        _positive(lepton_mass=m)
        k=higgs_z_barr_zee_kernel((m/higgs_mass_GeV)**2,(m/z_mass_GeV)**2)
        pref=alpha*muon_mass_GeV*g[1]*gf*weak/(16*math.pi**3*m)
        rows.append(dict(internal_lepton=name,a_mu=pref*k['value'],kernel=k,
            quadrature_error_estimate=abs(pref)*k['quadrature_error_estimate']))
    return dict(contributions=rows,a_mu_HZ_charged_leptons=math.fsum(r['a_mu'] for r in rows),
        source=WEAK_PRIMARY,equation='13 with fixed g_hmu*g_hf replacing m_mu*m_f/v²',
        fixed_Y_owner='ae31_c2_intrinsic_m4_lepton_action.charged_lepton_yukawa_operator',
        quark_HZ_included=False,whole_EW_evaluated=False,action_selected=False)
