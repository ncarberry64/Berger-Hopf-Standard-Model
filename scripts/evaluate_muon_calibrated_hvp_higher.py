#!/usr/bin/env python
"""Execute exact NLO HVP kernels against the frozen independently measured R."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_hvp_spectral import load_alphaqed26_spectrum
from bhsm.interface.muon_calibrated_hvp_higher import next_to_leading_hvp_pauli


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    raw=config_path.read_bytes()
    config_sha=hashlib.sha256(raw).hexdigest()
    if config_sha!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('retained metrological input changed')
    config=json.loads(raw)
    alpha=1/config['primary_measurements']['alpha_inverse_0']['value']
    m=config['selected_consumer_values']['m_mu_GeV']['value']
    me=config['selected_consumer_values']['m_e_GeV']['value']
    mt=config['primary_measurements']['tau_mass']['value']
    input_dir=ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input'
    spectrum=load_alphaqed26_spectrum(input_dir)
    def apply(s=spectrum,**kwargs):
        return next_to_leading_hvp_pauli(s,alpha,m,me,mt,**kwargs)
    fine=apply(order=48,spectral_order=32,endpoint_v=48,kernel_decimal_precision=110)
    medium=apply(order=32,spectral_order=20,endpoint_v=48,kernel_decimal_precision=110)
    endpoint=apply(order=48,spectral_order=32,endpoint_v=32,kernel_decimal_precision=110)
    coarse=copy.deepcopy(spectrum)
    for name in ['PQCD_1','PQCD_2']:
        for key in ['x','y','stat','sys']:
            coarse['blocks'][name][key]=coarse['blocks'][name][key][::2]
    interpolation=apply(coarse,order=48,spectral_order=32,endpoint_v=48,kernel_decimal_precision=110)
    # Literal mass sensitivity of these same kernels, not a chosen native mode.
    dm=config['selected_consumer_values']['m_mu_GeV']['input_only_standard_uncertainty_assuming_independent_primitives']
    up=next_to_leading_hvp_pauli(spectrum,alpha,m+dm,me,mt,order=32,spectral_order=20,endpoint_v=40)
    down=next_to_leading_hvp_pauli(spectrum,alpha,m-dm,me,mt,order=32,spectral_order=20,endpoint_v=40)
    d_alpha=3*fine['NLO_HVP']['value']/alpha
    d_m=(up['NLO_HVP']['value']-down['NLO_HVP']['value'])/(2*dm)
    packet=dict(classification='CALIBRATED_PRIMARY_SPECTRAL_NLO_TWO_CURRENT_APPLICATION',
                application=fine,
                numerical_verification={
                    'outer_orders':[32,48],
                    'spectral_orders':[20,32],
                    'quadrature_difference':abs(fine['NLO_HVP']['value']-medium['NLO_HVP']['value']),
                    'endpoint_coordinates':[32,48],
                    'endpoint_extension_difference':abs(fine['NLO_HVP']['value']-endpoint['NLO_HVP']['value']),
                    'pQCD_nodes_per_interval':[2401,4801],
                    'interpolation_difference':abs(fine['NLO_HVP']['value']-interpolation['NLO_HVP']['value']),
                    'class_quadrature_differences':{name:abs(row['value']-medium['classes'][name]['value'])
                        for name,row in fine['classes'].items()},
                    'classification':'numerical refinement estimates; not rigorous enclosures'},
                selected_input_sensitivity={
                    'derivative_alpha':d_alpha,'derivative_m_mu_GeV':d_m,
                    'alpha_standard_error_first_order':abs(d_alpha)*config['alpha_consumer']['standard_uncertainty_first_order'],
                    'muon_standard_error_first_order':abs(d_m)*dm,
                    'muon_mass_central_difference_step_GeV':dm,
                    'scope':'mass finite difference; alpha-cubed scaling exact at fixed masses/spectrum; shared metrology covariance not asserted'},
                input_config={'path':str(config_path.relative_to(ROOT)).replace('\\','/'),'sha256':config_sha,'bytes':len(raw),'modified':False},
                spectral_provenance_sha256=hashlib.sha256((input_dir/'provenance.json').read_bytes()).hexdigest(),
                kernel_provenance_sha256=hashlib.sha256((ROOT/'artifacts/muon_calibrated_hvp_higher_20261010/input/provenance.json').read_bytes()).hexdigest(),
                producer_source_sha256=hashlib.sha256((ROOT/'src/bhsm/interface/muon_calibrated_hvp_higher.py').read_bytes()).hexdigest(),
                measured_anomaly_used=False,SM_total_used=False,complete_native_remainder=False,
                complete_a_mu=None,complete_g_mu=None,action_selected=False,Gate7_closed=False)
    args.output.mkdir(parents=True,exist_ok=True)
    target=args.output/'hvp_higher.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                      'bytes':target.stat().st_size,'NLO_HVP':fine['NLO_HVP']['value'],
                      'spectral_error':fine['NLO_HVP']['spectral_error'],
                      'numerical_verification':packet['numerical_verification']},sort_keys=True))


if __name__=='__main__':main()
