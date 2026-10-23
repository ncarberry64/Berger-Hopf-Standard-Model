"""Evaluate true-E1 magnetic cubic, canonical, constraint and energy contacts."""
from __future__ import annotations
import argparse,json,sys
from hashlib import sha256
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs
from bhsm.interface.muon_magnetic_true_birth_mean_load import true_birth_mean_contact_application
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


def evaluate(directories):
    angular=retained_full_q_angular_space(ROOT);arrays={};rows=[];hashes={}
    for side,path in directories.items():
        print(json.dumps(dict(stage='true_E1_cubic_canonical_constraint_energy',side=side)),flush=True)
        inputs=load_magnetic_reached_mean_inputs(path,repository=ROOT)
        if inputs['receipt']['side']!=side:raise ValueError('same incoming/outgoing owner required')
        result=true_birth_mean_contact_application(inputs,repository=ROOT,angular=angular)
        birth=result['birth'];fields=birth['fields'];applied=result['application']
        hashes.update(birth['input_hashes'])
        for k,v in result.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        for k,v in applied.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        for k,v in fields.items():
            if isinstance(v,np.ndarray):arrays[side+'_'+k]=v
        for k in ('canonical_state','velocity','A_tau','Legendre_residual','Gauss_residual'):
            arrays[side+'_'+k]=birth[k]
        rows.append(dict(side=side,true_E1_endpoint_coefficients_used=True,
            response_time=fields['response_time'],coordinate_time=0.,profile=1.,profile_rate=0.,
            endpoint_receipt_sha256=birth['endpoint']['receipt_sha256'],
            Legendre_maximum_residual=float(np.max(abs(birth['Legendre_residual']))),
            Gauss_maximum_residual=float(np.max(abs(birth['Gauss_residual']))),
            norms={k:float(np.linalg.norm(result[k])) for k in
                ('mean_master_cotangent','canonical_velocity_contact','fixed_action_energy_contact',
                 'fixed_multiplier_constraint_contact','source_motion_velocity_work')},
            first_H_norm=float(np.linalg.norm(fields['first_H'])),
            first_H_rate_norm=float(np.linalg.norm(fields['first_H_rate'])),
            unused_At_rate_scope=fields['At_rate_zero_slot_scope']))
    if set(directories)=={'incoming','outgoing'}:
        for key in ('canonical_velocity_contact','fixed_canonical_velocity_contact',
                    'source_motion_canonical_velocity_contact'):
            arrays['paired_'+key]=arrays['incoming_'+key]-arrays['outgoing_'+key]
    sources=[record('src/bhsm/interface/muon_magnetic_true_birth_mean_load.py',
        ('true_birth_mean_contact_application','fixed_first_pair_action','canonical_energy_mixed_contact')),
        record('src/bhsm/interface/muon_magnetic_true_birth_fields.py',('true_magnetic_birth_fields','birth_constitutive_response')),
        record('src/bhsm/interface/muon_magnetic_source_mean_load.py',('magnetic_source_complete_mean_load',)),
        record('src/bhsm/interface/muon_electromagnetic_source_mean_load.py',('source_jet_motion_contact',)),
        record('src/bhsm/interface/muon_current_source_motion_cubic.py',('maxwell_cross_hessian','higgs_cross_hessian')),
        record('src/bhsm/interface/muon_birth_paired_field_endpoint.py',('paired_field_endpoint_rows',)),
        record('scripts/evaluate_muon_magnetic_true_birth_mean_load.py',('evaluate',))]
    for item in sources:hashes[item['path']]=item['sha256']
    if any(sha256((ROOT/name).read_bytes()).hexdigest()!=digest for name,digest in hashes.items()):
        raise RuntimeError('consumed action owner changed')
    return serial(dict(classification='EVALUATED_TRUE_E1_MAGNETIC_CUBIC_CANONICAL_CONSTRAINT_ENERGY_CONTACTS',
        input_hashes=hashes,source_records=sources,applications=rows,
        array_records={k:array_record(v) for k,v in arrays.items()},
        raw_coordinate_order='geometry100,gauge80,gauge_rate80,Hreal4,Hrate4',
        master_coordinate_order='x106,v106,y40',
        canonical_contact_equation='g_master=P^T complete rawload; g_v already belongs to canonical p; paired stored g_v is a source for event composition, not appended twice',
        fixed_action_energy_equation='E_AB=v_base*(D3L)_v,AB+D2L[u_A,V_B]+D2L[u_B,V_A]-D2L[u_A,u_B]',
        source_motion_energy_scope='separate velocity-work pullback; no nonlinear full-angular H-selected source chart inferred',
        all_future_dynamic_rate_slots_used=True,At_dot_used=False,
        source_motion_count=1,paired_derivative_divided_by_two=False,
        true_E1_endpoint_coefficients_used=True,source_cell_midpoint_velocities_substituted=False,
        canonical_first_state_is_reached_source_cell_state=True,
        source_first_state_reintegrated_on_true_endpoint_background=False,
        second_mean_birth_graph_or_global_geometry_transport_completed=False,
        quantum_loop_LSZ_or_complete_native_Pauli=False,
        error_scope='literal binary64 finite action third contractions and sourced E1 constitutive solve; continuum, quadrature and rounding not enclosed')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--incoming-response',type=Path,required=True)
    p.add_argument('--outgoing-response',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve previous applications')
    packet,arrays=evaluate(dict(incoming=a.incoming_response,outgoing=a.outgoing_response))
    data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('lossless split required')
    a.output.mkdir(parents=True);(a.output/'application.npz').write_bytes(data)
    packet['archive']=dict(path='application.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'result.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],applications=packet['applications'])),flush=True)


if __name__=='__main__':main()
