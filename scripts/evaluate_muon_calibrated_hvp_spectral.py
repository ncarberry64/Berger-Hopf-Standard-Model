#!/usr/bin/env python
"""Apply the primary source spectrum; never use an anomaly or SM total."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_hvp_spectral import (
    delta_alpha_had_spacelike_jet,
    leading_hvp_pauli,
    load_alphaqed26_spectrum,
)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    input_dir=ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input'
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    raw=config_path.read_bytes()
    config_sha=hashlib.sha256(raw).hexdigest()
    if config_sha!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('retained metrological configuration identity changed')
    config=json.loads(raw)
    alpha=1/config['primary_measurements']['alpha_inverse_0']['value']
    muon=config['selected_consumer_values']['m_mu_GeV']['value']
    spectrum=load_alphaqed26_spectrum(input_dir)
    fine=leading_hvp_pauli(spectrum,alpha,muon,order=32)
    low_order=leading_hvp_pauli(spectrum,alpha,muon,order=8)
    coarse=copy.deepcopy(spectrum)
    for name in ['PQCD_1','PQCD_2']:
        for key in ['x','y','stat','sys']:
            coarse['blocks'][name][key]=coarse['blocks'][name][key][::2]
    coarse_value=leading_hvp_pauli(coarse,alpha,muon,order=32)
    primary=json.loads((input_dir/'provenance.json').read_text(encoding='utf8'))
    published=primary['published_comparison']['standard_ee_source_nominal_LO']
    packet={
        'classification':'CALIBRATED_PRIMARY_SPECTRAL_TWO_CURRENT_APPLICATION',
        'LO_HVP':fine,
        'spacelike_photon_rows':{
            str(q):delta_alpha_had_spacelike_jet(spectrum,q,alpha,order=20)
            for q in [0,.01,.1,1.,10.,100.]},
        'numerical_verification':{
            'quadrature_orders':[8,32],
            'quadrature_difference':abs(fine['value']-low_order['value']),
            'resonance_component_differences':{
                name:abs(value-low_order['components'][name])
                for name,value in fine['components'].items() if name.startswith('RESONANCE')},
            'pQCD_nodes_per_interval':[2401,4801],
            'pQCD_interpolation_difference':abs(fine['value']-coarse_value['value']),
            'meaning':'finite numerical refinement estimates, not rigorous integration enclosures'},
        'source_nominal_comparison':{
            'nominal':published,'source_sigma':primary['published_comparison']['standard_ee_source_nominal_error'],
            'difference':fine['value']-published,
            'classification':'diagnostic comparison only; current raw release independently integrated, no center shift or anomaly fitting'},
        'tail':{
            'numerical_endpoint_GeV':1e6,
            'remaining_leading_asymptotic_estimate':fine['tail_asymptotic_estimate'],
            'scope':'fixed-order five-flavor source ultraviolet model; exact full-QCD upper enclosure not asserted',
            'included_as_exact_zero':False},
        'overlap':primary['overlap'],
        'input_config':{'path':str(config_path.relative_to(ROOT)).replace('\\','/'),
                        'sha256':config_sha,'bytes':len(raw),'modified':False},
        'input_provenance_sha256':hashlib.sha256((input_dir/'provenance.json').read_bytes()).hexdigest(),
        'producer_source_sha256':hashlib.sha256((ROOT/'src/bhsm/interface/muon_calibrated_hvp_spectral.py').read_bytes()).hexdigest(),
        'measured_anomaly_used':False,'measured_g_used':False,'SM_total_used':False,
        'action_selected':False,'Gate7_closed':False,'complete_native_remainder':False,
        'complete_a_mu':None,'complete_g_mu':None,'complete_magnetic_moment':None,
    }
    args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'hvp_spectral.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                      'bytes':target.stat().st_size,'LO_HVP':fine['value'],
                      'spectral_error':fine['spectral_error']},sort_keys=True))

if __name__=='__main__':main()
