"""Primary-kernel checks and CONTROL_ONLY finite algebra for local weak/decay terms."""
import hashlib
import importlib.util
import math
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
import pytest
import sympy as sp
from scipy.integrate import quad

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_weak_decay import (
    muon_decay_phase_space,muon_decay_one_loop_coefficient,
    muon_decay_two_loop_finite_mass,muon_decay_tau_vp,
    muon_lifetime_qed_factor,rematch_fermi_constant,
    electroweak_two_loop_fermionic_rest,electroweak_two_loop_vva_sectors,
    vva_perturbative_masspoint_shift,_vva_kinematic_weights,
)

INPUT=dict(alpha_0=1/137.035999206,muon_electron_ratio=206.76838,
    muon_tau_ratio=.10565842526040435/1.77709)
GF_INPUT=dict(INPUT,muon_mass_GeV=.10565842526040435,lifetime_seconds=2196980.3e-12,
    hbar_GeV_seconds=6.62607015e-34/(2*math.pi*1.602176634e-10))
WEAK_INPUT=dict(alpha_0=INPUT['alpha_0'],fermi_constant_GeV_inverse_squared=1.1663774240217165e-5,
    muon_mass_GeV=GF_INPUT['muon_mass_GeV'],tau_mass_GeV=1.77709,
    w_mass_GeV=80.3602,z_mass_GeV=91.1876,top_pole_mass_GeV=171.1)


def test_exact_phase_space_and_physical_mass_order():
    rho=1/INPUT['muon_electron_ratio'];x=rho*rho
    assert muon_decay_phase_space(rho)==pytest.approx(1-8*x-12*x*x*math.log(x)+8*x**3-x**4,abs=1e-16)
    assert (muon_decay_phase_space(rho)-1)*1e6==pytest.approx(-187.050652710,abs=2e-7)
    for bad in (0,1,float('nan'),float('inf')):
        with pytest.raises(ValueError):muon_decay_phase_space(bad)


def test_exact_finite_one_loop_matches_independent_2026_primary_value():
    # 2607.02657 Eq8, its own reference rho rather than selected optical rho.
    out=muon_decay_one_loop_coefficient(483633169e-11)
    finite=out['coefficient']-(25/8-math.pi**2/2)
    assert finite==pytest.approx(.00221421744,abs=8e-11)
    assert out['quadrature_error_estimate']<2e-10
    assert abs(out['exact_minus_expansion'])>1e-7


def test_finite_electron_two_loop_keeps_nonanalytic_linear_term():
    rho=1/INPUT['muon_electron_ratio'];out=muon_decay_two_loop_finite_mass(rho)
    assert out['powers']['1']==-5*math.pi**2*rho/4
    assert out['coefficient_correction']==pytest.approx(-.0791596557129,abs=1e-12)
    tiny=muon_decay_two_loop_finite_mass(1e-7)
    assert tiny['coefficient_correction']/1e-7==pytest.approx(-5*math.pi**2/4,rel=1e-4)
    assert out['rigorous_remainder_enclosure'] is None


def test_tau_lifetime_integral_sign_decoupling_and_no_muon_doublecount():
    physical=muon_decay_tau_vp(INPUT['muon_tau_ratio'])
    assert physical['coefficient']==pytest.approx(-.0005822871989,abs=2e-12)
    lighter=muon_decay_tau_vp(.06);heavier=muon_decay_tau_vp(.03)
    assert lighter['coefficient']<heavier['coefficient']<0
    assert .25<heavier['coefficient']/lighter['coefficient']<.4
    assert physical['muon_bubble_added'] is False


def test_additive_rate_accounting_and_known_third_order():
    q=muon_lifetime_qed_factor(**INPUT)
    total=1+q['delta_q0']+q['delta_q1']+q['delta_q2']+q['delta_q3']+q['current_hadronic_delta_q3_estimate']
    assert q['rate_factor']==pytest.approx(total,abs=2e-16)
    product=(1+q['delta_q0'])*(1+q['delta_q1']+q['delta_q2']+q['delta_q3'])
    assert abs(product-q['rate_factor'])>5e-7
    assert q['current_delta_q3']<0
    assert q['third_order']['coefficient']==pytest.approx(-18.22886050957,abs=1e-11)
    assert q['hadronic_third_order_estimate']['status']=='ESTIMATE_NOT_COMPLETED_INTEGRAL'
    assert q['W_propagator_correction_in_GF_definition'] is False


def test_os_ms_scheme_conversion_has_finite_constant_and_exact_series_identity():
    # CONTROL_ONLY symbolic power-series proof, no state or fitted coefficient.
    t,a1,a2,c1,c2,c3=sp.symbols('t a1 a2 c1 c2 c3')
    b=t*(1+a1*t+a2*t*t)
    transformed=sp.series(c1*b+c2*b*b+c3*b**3,t,0,4).removeO()
    strict=c1*t+(c2+a1*c1)*t*t+(c3+2*a1*c2+a2*c1)*t**3
    assert sp.expand(transformed-strict)==0
    q=muon_lifetime_qed_factor(**INPUT);L=2*math.log(INPUT['muon_electron_ratio'])
    assert q['charge_conversion']['coefficients']==pytest.approx([L/3,L*L/9+L/4+15/16])
    assert abs(q['rate_factor']-q['strict_alpha_0_order3_rate_factor'])<1e-8
    assert q['errors']['omitted_order_rate_allowance_estimate']>=abs(q['rate_factor']-q['strict_alpha_0_order3_rate_factor'])


def test_lifetime_reconstruction_and_dimensionful_hbar():
    out=rematch_fermi_constant(**GF_INPUT)
    GF=out['G_F_GeV_minus2'];F=out['lifetime_factor']['rate_factor']
    rate_GeV=GF*GF*GF_INPUT['muon_mass_GeV']**5*F/(192*math.pi**3)
    assert GF_INPUT['hbar_GeV_seconds']/rate_GeV==pytest.approx(GF_INPUT['lifetime_seconds'],rel=4e-16)
    assert GF==pytest.approx(1.1663774240217165e-5,rel=2e-13)
    assert abs(out['relative_lifetime_residual'])<3e-16
    assert out['measured_anomaly_used'] is False
    assert out['full_electroweak_matching_evaluated'] is False


def test_lifetime_and_mass_powers_with_independent_fixed_ratios():
    out=rematch_fermi_constant(**GF_INPUT);base=out['G_F_GeV_minus2']
    ratio=1.002
    t=rematch_fermi_constant(**dict(GF_INPUT,lifetime_seconds=GF_INPUT['lifetime_seconds']*ratio))
    m=rematch_fermi_constant(**dict(GF_INPUT,muon_mass_GeV=GF_INPUT['muon_mass_GeV']*ratio))
    assert t['G_F_GeV_minus2']/base==pytest.approx(ratio**(-.5),rel=3e-16)
    assert m['G_F_GeV_minus2']/base==pytest.approx(ratio**(-2.5),rel=3e-16)


@pytest.mark.parametrize('key,bad',[('alpha_0',.1),('muon_electron_ratio',1),('muon_tau_ratio',1),('alpha_0',float('nan'))])
def test_rate_input_guards(key,bad):
    with pytest.raises(ValueError):muon_lifetime_qed_factor(**dict(INPUT,**{key:bad}))


def test_fermionic_no_H_remainder_sign_and_literal_gammaZ_response():
    base=electroweak_two_loop_fermionic_rest(**WEAK_INPUT)
    old=electroweak_two_loop_fermionic_rest(**WEAK_INPUT,gamma_z_correlator=6.88)
    sw=1-(WEAK_INPUT['w_mass_GeV']/WEAK_INPUT['z_mass_GeV'])**2
    expected=-base['common_prefactor']*4*(1-4*sw)/3*.88
    assert old['a_mu_fermionic_rest_no_H']-base['a_mu_fermionic_rest_no_H']==pytest.approx(expected,rel=2e-14)
    assert base['a_mu_fermionic_rest_no_H']==pytest.approx(-4.530898135994572e-11,rel=3e-7)
    assert all(v<0 for v in base['contributions'].values())
    assert base['top_Yukawa_fitted'] is False and base['Higgs_diagrams_included'] is False


def test_fermionic_rest_top_pole_response_and_angle_guard():
    low=electroweak_two_loop_fermionic_rest(**dict(WEAK_INPUT,top_pole_mass_GeV=170))
    high=electroweak_two_loop_fermionic_rest(**dict(WEAK_INPUT,top_pole_mass_GeV=174))
    assert high['a_mu_fermionic_rest_no_H']<low['a_mu_fermionic_rest_no_H']
    with pytest.raises(ValueError):electroweak_two_loop_fermionic_rest(**dict(WEAK_INPUT,w_mass_GeV=100))


@pytest.mark.parametrize('q2',[1e-7,1,1e7,1e18])
def test_vva_kinematic_weights_match_primary_fractions_without_lost_half(q2):
    # CONTROL_ONLY kernel arithmetic; exact PDF Eq2 uses Q²/(2m_mu²) twice.
    with mp.workdps(60):
        mm=mp.mpf('.10565842526040435');mz=mp.mpf('91.1876');Q=mp.mpf(str(q2));z=Q/mm**2;W=mp.sqrt(1+4/z)
        refL=(1-z/2)*W+z/2
        refT=((2+z/2)*W-(3+z/2))*mz**2/(mz**2+Q)
    got=_vva_kinematic_weights(q2,float(mm),float(mz))
    assert got==pytest.approx([float(refL),float(refT)],rel=3e-15)


def test_vva_large_Q_chiral_suppression():
    q2=1e16;mm=.1;mz=90.
    L,T=_vva_kinematic_weights(q2,mm,mz)
    assert L/(3*mm*mm/q2)==pytest.approx(1,rel=1e-14)
    assert T/(3*mm*mm/q2*mz*mz/(mz*mz+q2))==pytest.approx(1,rel=1e-14)


def test_vva_mass_shift_against_independent_feynman_parameter_quadrature():
    # CONTROL_ONLY independent integration of Eq3, using the same physical
    # measured masses but a distinct angular integral rather than its closed form.
    x,w=np.polynomial.legendre.leggauss(160);x=(x+1)/2;w=w/2;u=x*(1-x)
    ms=1.77709;mr=1.77686;mm=WEAK_INPUT['muon_mass_GeV'];mz=WEAK_INPUT['z_mass_GeV']
    def integrand(y):
        Q=math.exp(y);z=Q/mm**2;W=math.sqrt(1+4/z)
        # Rationalized reference fractions, independently derived from PDF.
        d=4/(z*(W+1));cL=d*(W+2)/(W+1);cT=d*(2*W+1)/(W+1)*mz*mz/(mz*mz+Q)
        diff=np.dot(w,Q*u*(mr*mr-ms*ms)/((Q*u+ms*ms)*(Q*u+mr*mr)))
        return -2*Q*(cL+cT/2)*diff
    area,error=quad(integrand,-35,35,epsabs=2e-10,epsrel=2e-8,limit=200)
    pref=WEAK_INPUT['alpha_0']*WEAK_INPUT['fermi_constant_GeV_inverse_squared']/(24*math.sqrt(2)*math.pi**3)
    got=vva_perturbative_masspoint_shift(alpha_0=WEAK_INPUT['alpha_0'],fermi_constant_GeV_inverse_squared=WEAK_INPUT['fermi_constant_GeV_inverse_squared'],
        muon_mass_GeV=mm,z_mass_GeV=mz,fermion_mass_GeV=ms,reference_fermion_mass_GeV=mr,
        electric_charge=-1,weak_isospin=-.5,color_factor=1)
    assert got['a_mu_shift']==pytest.approx(pref*area,rel=3e-6,abs=3e-21)
    assert got['a_mu_shift']>0 and got['separately_physical_generation_sector'] is False


def test_vva_generation_integrals_not_whole_SM_total():
    args=dict(alpha_0=WEAK_INPUT['alpha_0'],fermi_constant_GeV_inverse_squared=WEAK_INPUT['fermi_constant_GeV_inverse_squared'],muon_mass_GeV=WEAK_INPUT['muon_mass_GeV'])
    out=electroweak_two_loop_vva_sectors(**args,top_pole_mass_GeV=171.1,tau_mass_GeV=1.77709)
    assert [r['generation'] for r in out['contributions']]==['u,d,e','c,s,mu','t,b,tau']
    assert out['a_mu_VVA']==pytest.approx(-1.432678603291614e-10,rel=1e-10)
    assert out['whole_EW_total_imported'] is False and out['selected_Higgs_Yukawa'] is False
    assert out['published_sector_covariance'] is None
    assert all(r['a_mu_shift']>0 for r in out['third_generation_perturbative_masspoint_shifts'])
    with pytest.raises(ValueError):electroweak_two_loop_vva_sectors(**args,top_pole_mass_GeV=171.1)


def test_higher_QED_source_and_old_packets_remain_pinned():
    expected={'src/bhsm/interface/muon_calibrated_higher_qed.py':'da58048f891504419159d558b44d4a0c6cb4cbf703aca7884dd515d88f99ae3a',
        'scripts/evaluate_muon_calibrated_higher_qed.py':'fde869addaf60d8c6b0323f1b39813d385a70baec9dc33feba45dd55ee8e8262',
        'artifacts/muon_calibrated_higher_qed_20261010/run_1/higher_qed.json':'4c1c5cb7ba7481b28c009adc9d8817cb6cd70c6d1f642616d4c703663ffc694b'}
    for rel,sha in expected.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==sha


@pytest.fixture(scope='module')
def evaluated_packet():
    spec=importlib.util.spec_from_file_location('weak_decay_producer',ROOT/'scripts/evaluate_muon_calibrated_weak_decay.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.evaluate()


def test_GF_primitive_gradient_chains_shared_electron_and_optical_mass(evaluated_packet):
    # Independent measured-primitive perturbation, including physical m_e and
    # m_mu reconstruction, rather than treating GF and m_mu independently.
    import json
    c=json.loads((ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json').read_text(encoding='utf8'))
    p=c['primary_measurements'];ai=p['alpha_inverse_0']['value'];R=p['R_infinity']['value'];r=p['muon_electron_mass_ratio']['value']
    tau=p['positive_muon_lifetime']['value'];mt=c['selected_consumer_values']['m_tau_GeV']['value']
    def get(a,ryd,ratio,life):
        me=2*6.62607015e-34*299792458*ryd*a*a/1.602176634e-10;m=me*ratio
        return rematch_fermi_constant(alpha_0=1/a,muon_electron_ratio=ratio,muon_tau_ratio=m/mt,
            muon_mass_GeV=m,lifetime_seconds=life*1e-12,hbar_GeV_seconds=float(c['unit_convention']['hbar_GeV_s']))['G_F_GeV_minus2']
    original=[ai,R,r,tau];gradient=evaluated_packet['input_uncertainty']['GF_vs_primitive_gradient'];h=1e-5
    for i,val in enumerate(original):
        plus=original.copy();minus=original.copy();plus[i]=val*math.exp(h);minus[i]=val*math.exp(-h)
        independent=(get(*plus)-get(*minus))/(2*h*val)
        assert gradient[i]==pytest.approx(independent,rel=2e-8)
    assert gradient[4]==0


def test_evaluated_weak_gradient_keeps_pole_MW_MZ_and_no_covariance_claim(evaluated_packet):
    u=evaluated_packet['local_EW_evaluated_subtotal_input_uncertainty']
    assert u['primitive_order'][-3:]==['MW_GeV','MZ_GeV','top_pole_GeV']
    assert len(u['gradient'])==9 and all(math.isfinite(x) for x in u['gradient'])
    assert all(x!=0 for x in u['gradient'][-3:])
    assert u['actual_cross_source_covariance'] is None
    assert u['standard_uncertainty_upper_over_all_correlations_plus']>=u['illustrative_independent_standard_uncertainty_plus']
    assert u['gamma_Z_correlator_derivative']<0


def test_omitted_weak_sectors_and_native_never_assigned_zero(evaluated_packet):
    p=evaluated_packet;missing=p['remaining_weak_sectors']
    assert missing['bosonic_two_loop'] is None and missing['quark_Hgamma_HZ'] is None
    assert missing['top_Higgs_Yukawa_from_pole_mass_assigned'] is False
    assert missing['enclosure'] is None
    assert missing['finite_order_allowance_estimate']==2*(19.96+1.50)*1e-11
    assert p['native_or_parent_lifetime_matching_correction'] is None
    assert p['full_native_response'] is None and p['full_native_overlap'] is None
    assert p['broader_BHSM_exact_tree_nu_lambda_matching_proved'] is False
    assert p['action_selected'] is False and p['Gate7_closed'] is False
    evaluated_sum=math.fsum((p['leading_EW_rematched']['a_mu_leading_EW'],p['fermionic_rest_no_H']['a_mu_fermionic_rest_no_H'],
        p['VVA_current_sectors']['a_mu_VVA'],p['fixed_Y_lepton_Hgamma']['a_mu_Hgamma_charged_leptons'],p['fixed_Y_lepton_HZ']['a_mu_HZ_charged_leptons']))
    assert p['local_EW_evaluated_sector_subtotal']==evaluated_sum
