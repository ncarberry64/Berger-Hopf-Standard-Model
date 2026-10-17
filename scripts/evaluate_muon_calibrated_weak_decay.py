#!/usr/bin/env python
"""Apply known muon-decay QED orders and separate non-Higgs weak sectors."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_weak_decay import (
    rematch_fermi_constant,muon_lifetime_rate_log_derivatives,
    electroweak_two_loop_fermionic_rest,electroweak_two_loop_vva_sectors,
)
from bhsm.interface.muon_calibrated_higher_qed import (
    leading_electroweak_pauli,fixed_yukawa_lepton_barr_zee_photon,
    fixed_yukawa_lepton_barr_zee_z,
)


def evaluate():
    path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('Selected measured-input configuration changed')
    core=ROOT/'src/bhsm/interface/muon_calibrated_higher_qed.py'
    if hashlib.sha256(core.read_bytes()).hexdigest()!='da58048f891504419159d558b44d4a0c6cb4cbf703aca7884dd515d88f99ae3a':
        raise ValueError('Preserved local higher-QED producer changed')
    config=json.loads(raw);p=config['primary_measurements'];v=config['selected_consumer_values']
    ai=p['alpha_inverse_0']['value'];r=p['muon_electron_mass_ratio']['value']
    ry=p['R_infinity']['value'];tau_ps=p['positive_muon_lifetime']['value']
    me=v['m_e_GeV']['value'];mm=v['m_mu_GeV']['value'];mtau=v['m_tau_GeV']['value'];mh=v['m_h_GeV']['value']
    hb=float(config['unit_convention']['hbar_GeV_s'])
    decay=rematch_fermi_constant(alpha_0=1/ai,muon_electron_ratio=r,muon_tau_ratio=mm/mtau,
        muon_mass_GeV=mm,lifetime_seconds=tau_ps*1e-12,hbar_GeV_seconds=hb)
    gf=decay['G_F_GeV_minus2'];F=decay['lifetime_factor']['rate_factor']
    response=muon_lifetime_rate_log_derivatives(alpha_0=1/ai,muon_electron_ratio=r,muon_tau_ratio=mm/mtau)
    d=response['derivative_log_inputs'];da=d['alpha_0'];dr=d['muon_electron_ratio'];dt=d['muon_tau_ratio']
    # m_e=2hc R_inf alpha_inverse^2/(GeV in J), m_mu=r*m_e.
    # The common alpha, electron mass, optical ratio and GF derivatives are
    # chained before multiplying any covariance or standard uncertainties.
    gf_grad=np.array([gf/ai*(-5+da/(2*F)-dt/F),
        gf/ry*(-2.5-dt/(2*F)),gf/r*(-2.5-(dr+dt)/(2*F)),
        -gf/(2*tau_ps),0.,gf*dt/(2*F*mtau)])
    mm_grad=np.array([2*mm/ai,mm/ry,mm/r,0.,0.,0.])
    std=np.asarray(config['uncertainty_and_correlations']['primitive_standard_uncertainties'])
    uncertainty=dict(primitive_order=config['uncertainty_and_correlations']['primitive_order'],
        GF_vs_primitive_gradient=gf_grad.tolist(),muon_mass_vs_primitive_gradient=mm_grad.tolist(),
        illustrative_GF_standard_uncertainty_independent_primitives=float(np.linalg.norm(gf_grad*std)),
        GF_standard_uncertainty_upper_over_all_primitive_correlations=float(np.sum(abs(gf_grad)*std)),
        actual_cross_source_covariance=None,rate_log_response=response,
        source_theory_and_truncation_errors_separate=True,
        scope='shared measured-input dependencies retained; independence illustrative, no complete uncertainty')
    mw,mz,top=80.3602,91.1876,171.1
    leading=leading_electroweak_pauli(fermi_constant_GeV_inverse_squared=gf,muon_mass_GeV=mm,w_mass_GeV=mw,z_mass_GeV=mz)
    lg=leading['derivatives']['GF']*gf_grad+leading['derivatives']['muon_mass']*mm_grad
    lg=np.r_[lg,leading['derivatives']['w_mass'],leading['derivatives']['z_mass']]
    ls=np.r_[std,.0099,.0021]
    leading['input_uncertainty']=dict(primitive_order=uncertainty['primitive_order']+['MW_GeV','MZ_GeV'],
        gradient=lg.tolist(),illustrative_independent_standard_uncertainty=float(np.linalg.norm(lg*ls)),
        standard_uncertainty_upper_over_all_correlations=float(np.sum(abs(lg)*ls)),
        actual_cross_source_covariance=None,
        shared_G_F_muon_mass_dependency_included=True,
        decay_matching_estimated_standard_uncertainty=leading['derivatives']['GF']*decay['decay_GF_combined_estimated_standard_uncertainty'],
        decay_matching_omitted_order_allowance_estimate=leading['derivatives']['GF']*decay['omitted_order_GF_allowance_estimate'])
    rest=electroweak_two_loop_fermionic_rest(alpha_0=1/ai,fermi_constant_GeV_inverse_squared=gf,
        muon_mass_GeV=mm,tau_mass_GeV=mtau,w_mass_GeV=mw,z_mass_GeV=mz,top_pole_mass_GeV=top)
    # Literal endpoint evaluations keep asymmetric published pole-mass errors;
    # no Monte Carlo mass is silently renamed a pole mass.
    top_up=math.sqrt(.4**2+.9**2+.7**2);top_down=math.sqrt(.4**2+.9**2+.3**2)
    def rest_top(m):
        return electroweak_two_loop_fermionic_rest(alpha_0=1/ai,fermi_constant_GeV_inverse_squared=gf,
            muon_mass_GeV=mm,tau_mass_GeV=mtau,w_mass_GeV=mw,z_mass_GeV=mz,top_pole_mass_GeV=m)['a_mu_fermionic_rest_no_H']
    rest['top_pole_input_response']=dict(mass_GeV=top,
        standard_uncertainty_plus_GeV=top_up,standard_uncertainty_minus_GeV=top_down,
        a_mu_at_plus_sigma=rest_top(top+top_up),a_mu_at_minus_sigma=rest_top(top-top_down),
        source='https://arxiv.org/abs/1905.02302',
        scheme='ATLAS tt+jet normalized differential cross-section NLO pole scheme',
        statistical_GeV=.4,systematic_GeV=.9,theory_plus_GeV=.7,theory_minus_GeV=.3,
        source_errors_combined_in_quadrature_as_diagnostic=True,top_Yukawa_assigned=False)
    vva=electroweak_two_loop_vva_sectors(alpha_0=1/ai,fermi_constant_GeV_inverse_squared=gf,muon_mass_GeV=mm,
        top_pole_mass_GeV=top,tau_mass_GeV=mtau,z_mass_GeV=mz)
    bz=fixed_yukawa_lepton_barr_zee_photon(alpha=1/ai,muon_mass_GeV=mm,higgs_mass_GeV=mh,lepton_masses_GeV=[mtau,mm,me])
    bz_z=fixed_yukawa_lepton_barr_zee_z(alpha=1/ai,muon_mass_GeV=mm,higgs_mass_GeV=mh,
        lepton_masses_GeV=[mtau,mm,me],w_mass_GeV=mw,z_mass_GeV=mz)
    weak_inputs=dict(W_mass=dict(value_GeV=mw,standard_uncertainty_GeV=.0099,
        source='https://arxiv.org/abs/2412.13872',edition='CMS2026 Nature652321',scheme='running-width'),
        Z_mass=dict(value_GeV=mz,standard_uncertainty_GeV=.0021,
        source='https://arxiv.org/abs/hep-ex/0509008',edition='LEP2006 Table2.13',scheme='running-width'),
        shared_W_Z_dependency='CMS W uses LEP Z closure; Table A.1 Z impact1.7MeV, signed covariance unavailable',
        top_pole=rest['top_pole_input_response'])
    remaining=dict(bosonic_two_loop=None,quark_Hgamma_HZ=None,
        top_Higgs_Yukawa_from_pole_mass_assigned=False,
        quark_Y_owner='ae31_c2_intrinsic_m4_lepton_action.action_composition_contract',
        quark_Y_status='up_down_Yukawa_terms_added=False; fixed ratios alone do not supply absolute transported action prefactors',
        bosonic_scope='ordinary reference bosonic result uses minimally matched gauge-Higgs/Goldstone counterterms; no full literal BHSM matching evaluated here',
        published_bosonic_reference=-19.96e-11,published_Higgs_reference=-1.50e-11,
        source='https://arxiv.org/abs/2503.04883',table='I, individual reference sectors only',
        finite_order_allowance_estimate=2*(19.96+1.50)*1e-11,
        estimate_basis='twice sum of absolute published omitted two-loop sectors; conditional minimal matched low-energy perturbative scale, not a bound on an arbitrary quark-Y completion',
        three_loop_NLL_estimated_standard_uncertainty=2e-12,
        enclosure=None,full_EW_two_loop_evaluated=False)
    subtotal=math.fsum((leading['a_mu_leading_EW'],rest['a_mu_fermionic_rest_no_H'],vva['a_mu_VVA'],
        bz['a_mu_Hgamma_charged_leptons'],bz_z['a_mu_HZ_charged_leptons']))
    # Derivatives of the actual evaluated sector sum, with the uncomputed
    # current-kernel mass changes retained in VVA's approximation allowance.
    # Difference each sector separately, avoiding cancellation of tiny Higgs
    # sensitivities against the much larger gauge weak contribution.
    cp=dict(alpha=1/ai,GF=gf,muon=mm,tau=mtau,higgs=mh,electron=me,MW=mw,MZ=mz,top=top)
    def weak_components(params):
        alpha,G,m,t,h,e,W,Z,T=(params[k] for k in ('alpha','GF','muon','tau','higgs','electron','MW','MZ','top'))
        L=leading_electroweak_pauli(fermi_constant_GeV_inverse_squared=G,muon_mass_GeV=m,w_mass_GeV=W,z_mass_GeV=Z)
        R=electroweak_two_loop_fermionic_rest(alpha_0=alpha,fermi_constant_GeV_inverse_squared=G,
            muon_mass_GeV=m,tau_mass_GeV=t,w_mass_GeV=W,z_mass_GeV=Z,top_pole_mass_GeV=T)
        V=electroweak_two_loop_vva_sectors(alpha_0=alpha,fermi_constant_GeV_inverse_squared=G,
            muon_mass_GeV=m,top_pole_mass_GeV=T,tau_mass_GeV=t,z_mass_GeV=Z)
        H=fixed_yukawa_lepton_barr_zee_photon(alpha=alpha,muon_mass_GeV=m,higgs_mass_GeV=h,lepton_masses_GeV=[t,m,e])
        HZ=fixed_yukawa_lepton_barr_zee_z(alpha=alpha,muon_mass_GeV=m,higgs_mass_GeV=h,
            lepton_masses_GeV=[t,m,e],w_mass_GeV=W,z_mass_GeV=Z)
        return (L['a_mu_leading_EW'],R['a_mu_fermionic_rest_no_H'],V['a_mu_VVA'],
            H['a_mu_Hgamma_charged_leptons'],HZ['a_mu_HZ_charged_leptons'])
    cg={};step=1e-4
    for name,value in cp.items():
        plus=dict(cp);minus=dict(cp);plus[name]=value*math.exp(step);minus[name]=value*math.exp(-step)
        cg[name]=math.fsum(a-b for a,b in zip(weak_components(plus),weak_components(minus)))/(2*step*value)
    me_grad=np.array([2*me/ai,me/ry,0.,0.,0.,0.])
    total_grad=cg['GF']*gf_grad+cg['muon']*mm_grad+cg['electron']*me_grad
    total_grad[0]-=cg['alpha']/ai**2;total_grad[4]+=cg['higgs'];total_grad[5]+=cg['tau']
    total_grad=np.r_[total_grad,cg['MW'],cg['MZ'],cg['top']]
    ext_plus=np.r_[std,.0099,.0021,top_up];ext_minus=np.r_[std,.0099,.0021,top_down]
    total_uncertainty=dict(primitive_order=uncertainty['primitive_order']+['MW_GeV','MZ_GeV','top_pole_GeV'],
        gradient=total_grad.tolist(),evaluated_consumer_derivatives=cg,consumer_central_log_step=step,
        illustrative_independent_standard_uncertainty_plus=float(np.linalg.norm(total_grad*ext_plus)),
        illustrative_independent_standard_uncertainty_minus=float(np.linalg.norm(total_grad*ext_minus)),
        standard_uncertainty_upper_over_all_correlations_plus=float(np.sum(abs(total_grad)*ext_plus)),
        standard_uncertainty_upper_over_all_correlations_minus=float(np.sum(abs(total_grad)*ext_minus)),
        standard_uncertainties_plus=ext_plus.tolist(),standard_uncertainties_minus=ext_minus.tolist(),
        actual_cross_source_covariance=None,
        decay_theory_estimated_standard_uncertainty=abs(cg['GF'])*decay['decay_GF_combined_estimated_standard_uncertainty'],
        decay_omitted_order_allowance_estimate=abs(cg['GF'])*decay['omitted_order_GF_allowance_estimate'],
        gamma_Z_correlator_derivative=-rest['common_prefactor']*4*(1-4*rest['sin_squared_theta_W'])/3,
        scope='all literal evaluated weak sectors and shared primitive dependencies; uncomputed VVA shapes and theory estimates separate; not full BHSM uncertainty')
    producer=ROOT/'src/bhsm/interface/muon_calibrated_weak_decay.py'
    return dict(classification='CALIBRATED_DECAY_REMATCH_AND_SELECTED_LOCAL_WEAK_SECTORS',
        decay_rematching=decay,input_uncertainty=uncertainty,
        GF_old_provisional_value=v['G_F_GeV_minus2']['value'],
        GF_relative_shift_from_frozen_provisional=gf/v['G_F_GeV_minus2']['value']-1,
        leading_EW_rematched=leading,fermionic_rest_no_H=rest,VVA_current_sectors=vva,
        fixed_Y_lepton_Hgamma=bz,fixed_Y_lepton_HZ=bz_z,
        local_EW_evaluated_sector_subtotal=subtotal,
        local_EW_evaluated_subtotal_input_uncertainty=total_uncertainty,
        local_subtotal_accounting='leading EW+VVA+f-rest,noH+literal fixed-Y lepton Hgamma/HZ; preserved scalar1 and QED1-5 excluded',
        remaining_weak_sectors=remaining,additional_weak_measurements=weak_inputs,
        calibrated_GF_scope='operational low-energy V-A Fermi coefficient extracted from selected lifetime, pole mass and specified local QED/hadronic decay corrections',
        broader_BHSM_exact_tree_nu_lambda_matching_proved=False,
        native_or_parent_lifetime_matching_correction=None,
        existing_higher_QED_packet_modified=False,measured_muon_anomaly_used=False,
        full_native_response=None,full_native_overlap=None,complete_a_mu=None,
        complete_uncertainty=False,action_selected=False,Gate7_closed=False,
        selected_input_config=dict(path=str(path.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),
        sources=[dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in (producer,Path(__file__),core)])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    packet=evaluate();args.output.mkdir(parents=True,exist_ok=True);target=args.output/'weak_decay.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,
        GF=packet['decay_rematching']['G_F_GeV_minus2'],EW_subtotal=packet['local_EW_evaluated_sector_subtotal']),sort_keys=True))


if __name__=='__main__':main()
