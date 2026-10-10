#!/usr/bin/env python
"""Evaluate new alpha³--alpha⁵ local terms; reuse the frozen local subtotal."""
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
from bhsm.interface.muon_calibrated_higher_qed import (
    calibrated_higher_qed,fixed_yukawa_lepton_barr_zee_photon,
    leading_electroweak_pauli,fixed_yukawa_lepton_barr_zee_z,
)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    inputs=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    baseline=ROOT/'artifacts/muon_calibrated_pauli_20261009/run_1/calibrated_pauli.json'
    raw=inputs.read_bytes(); previous=baseline.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('Recorded calibrated input configuration changed')
    if hashlib.sha256(previous).hexdigest()!='20a4b5a169439f2db2ff8d37c9746bb7a43c6887a266d6c3e5262d8500fad419':
        raise ValueError('Preserved two-loop plus fixed-Y scalar subtotal changed')
    config=json.loads(raw); old=json.loads(previous)
    values={k:v['value'] for k,v in config['selected_consumer_values'].items()}
    primitive=config['primary_measurements']
    ai=primitive['alpha_inverse_0']['value'];re=primitive['muon_electron_mass_ratio']['value']
    mt=values['m_tau_GeV'];mm=values['m_mu_GeV'];rh=primitive['R_infinity']['value']
    qed=calibrated_higher_qed(alpha=1/ai,muon_electron_ratio=re,muon_tau_ratio=mm/mt)
    de=qed['derivative_log_muon_electron_ratio'];dt=qed['derivative_log_muon_tau_ratio']
    gradient=np.array([-qed['derivative_alpha']/ai**2+2*dt/ai,dt/rh,(de+dt)/re,0.,0.,-dt/mt])
    std=np.asarray(config['uncertainty_and_correlations']['primitive_standard_uncertainties'])
    input_error=dict(primitive_order=config['uncertainty_and_correlations']['primitive_order'],
        gradient=gradient.tolist(),
        illustrative_standard_uncertainty_independent_primitives=float(np.linalg.norm(gradient*std)),
        standard_uncertainty_upper_over_all_primitive_correlations=float(np.sum(abs(gradient)*std)),
        measured_cross_source_covariance=None,
        C4_C5_masspoint_uncertainty_accounted_in_approximation_allowance=True,
        scope='linear C3 mass dependencies and alpha dependence; no full-observable uncertainty')
    bz=fixed_yukawa_lepton_barr_zee_photon(alpha=1/ai,muon_mass_GeV=mm,
        higgs_mass_GeV=values['m_h_GeV'],lepton_masses_GeV=[mt,mm,values['m_e_GeV']])
    mw,mz=80.3602,91.1876
    weak=leading_electroweak_pauli(fermi_constant_GeV_inverse_squared=values['G_F_GeV_minus2'],
        muon_mass_GeV=mm,w_mass_GeV=mw,z_mass_GeV=mz)
    bz_z=fixed_yukawa_lepton_barr_zee_z(alpha=1/ai,muon_mass_GeV=mm,
        higgs_mass_GeV=values['m_h_GeV'],lepton_masses_GeV=[mt,mm,values['m_e_GeV']],
        w_mass_GeV=mw,z_mass_GeV=mz)
    jac=np.asarray(config['uncertainty_and_correlations']['consumer_vs_primitive_jacobian'])
    order=config['uncertainty_and_correlations']['consumer_order']
    weak_grad=weak['derivatives']['GF']*jac[order.index('G_F_GeV_minus2')]
    weak_grad+=weak['derivatives']['muon_mass']*jac[order.index('m_mu_GeV')]
    weak_grad=np.r_[weak_grad,weak['derivatives']['w_mass'],weak['derivatives']['z_mass']]
    weak_std=np.r_[std,.0099,.0021]
    weak['input_uncertainty']=dict(gradient=weak_grad.tolist(),
        illustrative_independent_primitive_standard_uncertainty=float(np.linalg.norm(weak_grad*weak_std)),
        standard_uncertainty_upper_over_all_primitive_correlations=float(np.sum(abs(weak_grad)*weak_std)),
        actual_cross_source_covariance=None,GF_scope=config['selected_consumer_values']['G_F_GeV_minus2']['classification'])
    weak_inputs=dict(W_mass=dict(value_GeV=mw,standard_uncertainty_GeV=.0099,
        source='https://arxiv.org/abs/2412.13872',edition='CMS2026 Nature652321; arxiv2412.13872',
        scheme='running-width',measured_anomaly_used=False),
        Z_mass=dict(value_GeV=mz,standard_uncertainty_GeV=.0021,
            source='https://arxiv.org/abs/hep-ex/0509008',edition='LEP2006 Table2.13 without lepton universality',
            scheme='running-width'),
        dependency='CMS W mass uses LEP Z for its closure uncertainty: TableA.1 impact1.7MeV. Signed W/Z covariance not supplied; independence is illustrative only.',
        no_electroweak_fit_or_measured_muon_anomaly_selected=True)
    packet=dict(classification='CALIBRATED_LOCAL_HIGHER_QED_AND_FIXED_Y_LEPTON_HGAMMA_APPLICATION',
        qed=qed,input_uncertainty=input_error,fixed_Y_charged_lepton_Hgamma_two_loop=bz,
        leading_EW=weak,additional_weak_measurements=weak_inputs,fixed_Y_charged_lepton_HZ_two_loop=bz_z,
        prior_subtotal=dict(value=.0011655419088320725,sha256=hashlib.sha256(previous).hexdigest(),
            path=str(baseline.relative_to(ROOT)).replace('\\','/'),reused=True,rerun=False),
        local_QED_through_alpha5_plus_preserved_fixed_Y_Higgs_one_loop=.0011655419088320725+qed['increment'],
        Hgamma_lepton_term_separately_evaluated_not_yet_summed=True,
        completed_native_response=None,complete_a_mu=None,complete_g_mu=None,
        complete_magnetic_moment=None,complete_uncertainty=False,
        action_selected=False,Gate7_closed=False,measured_muon_anomaly_used=False,
        input_config=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),
        producer_source=dict(sha256=hashlib.sha256((ROOT/'src/bhsm/interface/muon_calibrated_higher_qed.py').read_bytes()).hexdigest()),
        execution='python scripts/evaluate_muon_calibrated_higher_qed.py --output <new-directory>')
    args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'higher_qed.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                         bytes=target.stat().st_size,increment=qed['increment']),sort_keys=True))


if __name__=='__main__':main()
