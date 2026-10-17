"""Fresh sourced fixed-Y mass, contact, and both photon heat insertions."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_native_reached_response_heat import retained_current_reached_response,reached_fixed_y_source_vertices,reached_first_response_heat_core
from bhsm.interface.muon_native_coupled_source_heat import corrected_first_response_heat_application


def evaluate():
    response=retained_current_reached_response(ROOT);rows=[];arrays={}
    for count in (5,9,17):
        print(json.dumps(dict(stage='fresh_coupled_response_heat',time_nodes=count)),flush=True)
        core=reached_first_response_heat_core(response,time_nodes=np.linspace(response['time_shift'],0,count),quadrature_order=4)
        row=corrected_first_response_heat_application(core,4.7240808471919143e-8,integrate_cutoff=True)
        row['normalization']='currentTb moving b duals plus fixedY actual fresh H80 response; no repeated Tb,QNORM,e orfamily/statistics factor'
        for family,value in row['families'].items():
            for name,component in value['components'].items():
                for key in ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion','reached_first_response_pair'):
                    arrays[f'nodes_{count}_family_{family}_{name}_{key}']=component[key]
        rows.append(dict(time_nodes=count,application=row,
            spectral_minimum=min(float(f['n0_eigenvalues'][0]) for f in core['families'].values()),
            full_intermediate_mode_counts={family:{n:len(shell['eigenvalues']) for n,shell in f['intermediate_shells'].items()} for family,f in core['families'].items()}))
    refinements=[]
    for old,new in zip(rows[:-1],rows[1:]):
        by_family={}
        for f in ('1','2'):
            by_family[f]={}
            for name in ('gauge','scalar','interference'):
                a=old['application']['families'][f]['components'][name]['reached_first_response_pair']
                b=new['application']['families'][f]['components'][name]['reached_first_response_pair'];norm=float(np.linalg.norm(b))
                by_family[f][name]=dict(absolute_Frobenius_difference=float(np.linalg.norm(a-b)),relative_Frobenius_difference=float(np.linalg.norm(a-b)/norm) if norm else None)
        refinements.append(dict(coarse_nodes=old['time_nodes'],fine_nodes=new['time_nodes'],families=by_family))
    t=response['times']+response['time_shift'];vertex=[reached_fixed_y_source_vertices(response,x) for x in t]
    arrays.update(response_times=response['times'],coordinate_times=t,
        current_T_b=np.array([v['current_T_b'] for v in vertex]),source_profile=np.array([v['profile'] for v in vertex]),
        actual_complex_H_response=np.array([v['complex_H_response'] for v in vertex]),
        cut_b_source_coefficients=response['cut_b_source_coefficients'])
    packet=dict(classification='EVALUATED_FRESH_CURRENT_NORMALIZED_COUPLED_FIRST_RESPONSE_HEAT_PAIR',
        consumed_input_records=response['source_records'],
        source_records=[record('src/bhsm/interface/muon_native_reached_response_heat.py',('retained_current_reached_response','reached_fixed_y_source_vertices','reached_first_response_heat_core')),
            record('scripts/evaluate_muon_native_reached_response_heat.py',('evaluate',)),
            record('src/bhsm/interface/muon_native_coupled_source_heat.py',('_first_response_blocks','corrected_first_response_heat_application'))],
        heat_rows=rows,temporal_refinement=refinements,
        fresh_H_response_norm=float(np.linalg.norm(response['H80'])),fresh_H_rate_norm=float(np.linalg.norm(response['H80_rate'])),
        gauge_source_normalization='beta(t)=Tb(currentR4)*fixed fresh currentcomponent u_hat, compact pulse imposed once by actual retarded producer',
        H_response_normalization='actual coupled scalar relative8 to same Maxwell action; fixedY mass applied once',
        physical_kappa1_unassigned=True,physical_cutoff_selected=False,
        cutoff_parameter=4.7240808471919143e-8,cutoff_scope='numerical centralprobe retained from original finitecore heat, not i/r formation',
        positive_Hilbert_n0_partial_not_full_supertrace=True,
        original_Q8_primal_or_mean_response_substituted=False,
        genuine_mixed_H_geometry_domain_jet_evaluated=False,
        whole_native_completion_overlap_or_Pauli_evaluated=False,
        middle_minus_light_subtraction_error_enclosed=False,
        actual_new_reached_cubic_mean_source_next=True,
        array_records={k:array_record(a) for k,a in arrays.items()})
    return serial(packet),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate();archive=deterministic_npz(arrays)
    if len(archive)>10*1024**2:raise ValueError('preserve arrays; split losslessly')
    args.output.mkdir(parents=True);(args.output/'reached_source_heat.npz').write_bytes(archive)
    packet['archive']=dict(path='reached_source_heat.npz',bytes=len(archive),sha256=sha256(archive).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(args.output/'reached_source_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),receipt_bytes=len(raw),archive=packet['archive']),sort_keys=True))


if __name__=='__main__':main()
