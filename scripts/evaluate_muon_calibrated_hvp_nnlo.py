#!/usr/bin/env python
"""Execute complete published NNLO HVP kernel classes at declared precision."""
from pathlib import Path
import argparse,copy,hashlib,json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_calibrated_hvp_spectral import load_alphaqed26_spectrum
from bhsm.interface.muon_calibrated_hvp_nnlo import next_to_next_to_leading_hvp_pauli,COEFFICIENT_SHA256


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json';raw=config_path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!='0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da':
        raise ValueError('retained metrological configuration changed')
    config=json.loads(raw)
    alpha=1/config['primary_measurements']['alpha_inverse_0']['value']
    m=config['selected_consumer_values']['m_mu_GeV']['value'];me=config['selected_consumer_values']['m_e_GeV']['value']
    input_dir=ROOT/'artifacts/muon_calibrated_hvp_spectral_20261010/input'
    spectrum=load_alphaqed26_spectrum(input_dir)
    def apply(s=spectrum,**kwargs):return next_to_next_to_leading_hvp_pauli(s,alpha,m,me,**kwargs)
    fine=apply(order=40,spectral_order=16,double_order=32,endpoint_v=40)
    coarse=apply(order=24,spectral_order=8,double_order=16,endpoint_v=32)
    interpolation=copy.deepcopy(spectrum)
    for name in ['PQCD_1','PQCD_2']:
        for key in ['x','y','stat','sys']:interpolation['blocks'][name][key]=interpolation['blocks'][name][key][::2]
    interp=apply(interpolation,order=40,spectral_order=16,double_order=32,endpoint_v=40)
    packet=dict(classification='CALIBRATED_SAME_SPECTRUM_COMPLETE_STANDARD_NNLO_HVP_CLASSES',application=fine,
                numerical_verification={
                    'outer_orders':[24,40],'spectral_orders':[8,16],'double_orders':[16,32],
                    'endpoint_coordinates':[32,40],
                    'refinement_difference':abs(fine['NNLO_HVP']['value']-coarse['NNLO_HVP']['value']),
                    'class_refinement_differences':{n:abs(r['value']-coarse['classes'][n]['value']) for n,r in fine['classes'].items()},
                    'pQCD_nodes_per_interval':[2401,4801],
                    'interpolation_difference':abs(fine['NNLO_HVP']['value']-interp['NNLO_HVP']['value']),
                    'scope':'numerical estimates; primary kernel approximation and omitted tau allowances remain separate'},
                selected_alpha_sensitivity={'derivative_alpha':4*fine['NNLO_HVP']['value']/alpha,
                    'standard_error_first_order':abs(4*fine['NNLO_HVP']['value']/alpha)*config['alpha_consumer']['standard_uncertainty_first_order']},
                input_config={'path':str(config_path.relative_to(ROOT)).replace('\\','/'),'sha256':sha,'modified':False},
                spectral_provenance_sha256=hashlib.sha256((input_dir/'provenance.json').read_bytes()).hexdigest(),
                coefficient_sha256=COEFFICIENT_SHA256,
                kernel_provenance_sha256=hashlib.sha256((ROOT/'artifacts/muon_calibrated_hvp_nnlo_20261010/input/provenance.json').read_bytes()).hexdigest(),
                producer_source_sha256=hashlib.sha256((ROOT/'src/bhsm/interface/muon_calibrated_hvp_nnlo.py').read_bytes()).hexdigest(),
                measured_anomaly_used=False,SM_total_used=False,complete_native_remainder=False,
                complete_a_mu=None,complete_g_mu=None,action_selected=False,Gate7_closed=False)
    args.output.mkdir(parents=True,exist_ok=True);target=args.output/'hvp_nnlo.json'
    target.write_text(json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'path':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                      'NNLO_HVP':fine['NNLO_HVP']['value'],'spectral_error':fine['NNLO_HVP']['spectral_error'],
                      'numerical_verification':packet['numerical_verification']},sort_keys=True))


if __name__=='__main__':main()
