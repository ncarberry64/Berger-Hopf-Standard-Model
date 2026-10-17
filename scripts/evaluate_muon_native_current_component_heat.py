"""Fresh current angular response, moving source, and fixed-core heat pair."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_native_coupled_source_heat import retained_corrected_scalar_photon_response
from bhsm.interface.muon_native_current_component_heat import current_geometric_photon_component,current_component_dual_response,current_component_source_history,component_response_fermion_image,current_component_response_heat_core
from bhsm.interface.muon_native_product_factor_graph import finite_eight_q_cutoff_heat_application


def evaluate():
    response=retained_corrected_scalar_photon_response(ROOT)
    component=current_geometric_photon_component(response,0.)
    solved=current_component_dual_response(component,multipliers=(1.25,2.,4.));chosen=solved['records'][0]
    times=np.linspace(response['time_shift'],0,385)
    history=current_component_source_history(response,component,chosen,times)
    image=component_response_fermion_image(component,chosen)
    arrays={k:component[k] for k in ('K_per_kappa1','source_inclusion','matrix_polynomial','coefficient_values',
        'coefficient_geometric_jacobian','coefficient_geometric_hessians','T_b_geometric_gradient','T_b_geometric_hessian',
        'geometric_pairing_gradient','geometric_pairing_hessian')}
    arrays.update({k:v for k,v in history.items() if isinstance(v,np.ndarray)})
    arrays['unit_radius_b_source_image']=image['unit_radius_b_source_image']
    arrays['source_directed_enriched_frame']=solved['independent_frame']
    for i,row in enumerate(solved['records']):
        for k in ('basis_response','basis_residual','return_basis'):
            arrays[f'component_probe_{i}_{k}']=row[k]
    cutoff=4.7240808471919143e-8
    heat=[]
    for count in (5,9,17):
        print(json.dumps(dict(stage='fresh_response_fixed_core_heat',time_nodes=count)),flush=True)
        core=current_component_response_heat_core(response,component,chosen,time_nodes=np.linspace(response['time_shift'],0,count),
            quadrature_order=4,family_indices=(1,2))
        applied=finite_eight_q_cutoff_heat_application(core,cutoff)
        for f,row in applied['families'].items():
            for k in ('integrated_source_square_contact','integrated_ordered_two_insertion','integrated_opposite_order_two_insertion','integrated_paired_heat_mixed'):
                arrays[f'heat_nodes_{count}_family_{f}_{k}']=row[k]
        heat.append(dict(time_nodes=count,cutoff_application=applied,
            positive_spectral_minimum=min(float(x['n0_eigenvalues'][0]) for x in core['families'].values()),
            actual_intermediate_mode_counts={f:{n:len(s['eigenvalues']) for n,s in row['intermediate_shells'].items()} for f,row in core['families'].items()}))
    refinement=[]
    for old,new in zip(heat[:-1],heat[1:]):
        rows={}
        for f in ('1','2'):
            a=old['cutoff_application']['families'][f]['integrated_paired_heat_mixed'];b=new['cutoff_application']['families'][f]['integrated_paired_heat_mixed']
            rows[f]=dict(absolute_Frobenius_difference=float(np.linalg.norm(a-b)),relative_Frobenius_difference=float(np.linalg.norm(a-b)/np.linalg.norm(b)))
        refinement.append(dict(coarse_nodes=old['time_nodes'],fine_nodes=new['time_nodes'],families=rows))
    refs=[record('src/bhsm/interface/muon_native_current_component_heat.py',('current_geometric_photon_component','current_component_dual_response','current_component_source_history','current_component_response_heat_core')),
        record('scripts/evaluate_muon_native_current_component_heat.py',('evaluate',)),
        record('src/bhsm/interface/muon_native_photon_response.py',('source_directed_component_response',)),
        record('src/bhsm/interface/muon_parent_maxwell_geometry_weak.py',('geometric_connection_coefficient_jets',)),
        record('src/bhsm/interface/muon_parent_maxwell_full_q_application.py',('retained_full_q_angular_space','full_q_reference_operators')),
        record('src/bhsm/interface/muon_native_product_factor_graph.py',('_family_shell_heat_forms','_family_source_heat_blocks','finite_eight_q_cutoff_heat_application'))]
    result=dict(classification='EVALUATED_CURRENT_NORMALIZED_ANGULAR_COMPONENT_RESPONSE_AND_FULL_REACHED_FIXED_CORE_HEAT',
        consumed_input_records=response['source_records'],source_records=refs,
        current_component={k:v for k,v in component.items() if not isinstance(v,np.ndarray) and k not in ('angular','intrinsic_geometry')},
        source_directed_response={k:v for k,v in solved.items() if k not in ('independent_frame','records','current')},
        response_probes=[{k:v for k,v in x.items() if not isinstance(v,np.ndarray)} for x in solved['records']],
        consumed_component_probe=0,source_history={k:v for k,v in history.items() if not isinstance(v,np.ndarray)},
        heat_applications=heat,heat_temporal_refinement=refinement,
        cutoff_probe=cutoff,physical_cutoff_selected=False,
        coupled_first_response_to_new_reached_columns_included=False,
        native_mean_contact_from_original_Q8_borrowed=False,
        actual_mode_current_covector_or_Pauli_projector_selected=False,
        full_principal_A0_or_native_response_evaluated=False,
        source_directed_consumer='the available current dual columns require u0†R u0; original Q8 return is not substituted',
        relative_family_subtraction_error_enclosed=False,
        heat_scope='positive Hilbert n0 partial with full n1/n3 two-insertion images, declared outgoing numerical Dirichlet core; not full graded native trace',
        array_records={k:array_record(v) for k,v in arrays.items()})
    return serial(result),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier applications; use a new output path')
    packet,arrays=evaluate();groups={}
    # Full source histories are separate, complete archives below the cap.
    for k,v in arrays.items():
        group=('source_Q' if k=='full400_source_Q' else 'source_Qdot' if k=='full400_source_Qdot' else
            'source_jets' if k.startswith('source_normal_') else 'component_and_heat')
        groups.setdefault(group,{})[k]=v
    records=[];args.output.mkdir(parents=True)
    for group,values in groups.items():
        raw=deterministic_npz(values)
        if len(raw)>10*1024**2:raise ValueError('preserve complete arrays; split this archive losslessly')
        name=group+'.npz';(args.output/name).write_bytes(raw);records.append(dict(path=name,bytes=len(raw),sha256=sha256(raw).hexdigest()))
    packet['archives']=records;raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    (args.output/'current_component_heat.json').write_bytes(raw)
    print(json.dumps(dict(receipt_bytes=len(raw),receipt_sha256=sha256(raw).hexdigest(),archives=records),sort_keys=True))


if __name__=='__main__':main()
