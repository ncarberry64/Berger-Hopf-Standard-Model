"""Execute reached two-time photon-action and open-lepton magnetic columns."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_native_two_time_green import load_executed_magnetic_green_form,retarded_boundary_green_application,continue_canonical_green_across_birth,apply_reached_canonical_source
from bhsm.interface.muon_magnetic_retarded_lepton import retarded_magnetic_lepton_application,reached_lorentz_magnetic_vertices
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile


def _arrays(value,prefix,output):
    if isinstance(value,np.ndarray):output[prefix]=value
    elif isinstance(value,dict):
        for name,child in value.items():_arrays(child,prefix+'_'+name,output)


def evaluate(directories):
    forms={side:load_executed_magnetic_green_form(path,repository=ROOT) for side,path in directories.items()}
    arrays={};hashes={};rows=[];angular=retained_full_q_angular_space(ROOT)
    for f in forms.values():hashes.update(f['input_hashes'])
    incoming,outgoing=forms['incoming'],forms['outgoing'];T=incoming['final_time']
    for channel in ('value','rate'):
        print(json.dumps(dict(stage='two_time_Euler_Gauss_Green',channel=channel)),flush=True)
        result=retarded_boundary_green_application(incoming,T/4,np.linspace(0,T,17),channel=channel)
        continuation=continue_canonical_green_across_birth(result,outgoing,np.linspace(0,outgoing['final_time'],17))
        _arrays(result,'incoming_'+channel,arrays);_arrays(continuation,'outgoing_'+channel,arrays)
        rows.append(dict(operator='reached_Euler_Gauss_Green',channel=channel,
            incoming_phase_norm=float(np.linalg.norm(result['phase_kernel'])),
            instantaneous_Gauss_contact_norm=float(np.linalg.norm(result['instantaneous_Gauss_contact'])),
            outgoing_phase_norm=float(np.linalg.norm(continuation['phase_kernel'])),
            canonical_birth_jump_norm=continuation['canonical_birth_jump_norm'],
            quantum_covariance_claimed=False))
    replay=apply_reached_canonical_source(incoming,lambda t:magnetic_turn_on_profile(t,T/4),
        observation_times=incoming['inputs']['source']['times'])
    indices=[int(np.flatnonzero(incoming['inputs']['times']==t)[0]) for t in replay['times']]
    reference=incoming['inputs']['phase']['state'][indices,:,:3]
    replay_relative=float(np.linalg.norm(replay['phase']-reference)/(1+np.linalg.norm(reference)))
    _arrays(replay,'source_channel_replay',arrays)
    for side,f in forms.items():
        print(json.dumps(dict(stage='actual_open_lepton_magnetic_Duhamel',side=side)),flush=True)
        result=retarded_magnetic_lepton_application(f['inputs'],angular)
        vertices=reached_lorentz_magnetic_vertices(f['inputs'])
        _arrays(result,side+'_lepton',arrays)
        for key in ('times','magnetic_Hcan_vertex','spatial_vertex','temporal_vertex','fixed_Y_H_vertex'):
            arrays[side+'_open_'+key]=vertices[key]
        rows.append(dict(operator='open_Lorentz_lepton_retarded_source',side=side,
            unitary_transport_defect=result['unitary_transport_defect'],
            actual_source_image_dimensions=result['complete_source_image_dimensions'],
            source_response_norms={n:float(np.linalg.norm(a)) for n,a in result['magnetic_open_fermion_response'].items()},
            quantum_loop_or_LSZ_claimed=False))
    sources=[record('src/bhsm/interface/muon_native_two_time_green.py',('load_executed_magnetic_green_form','retarded_boundary_green_application','continue_canonical_green_across_birth','apply_reached_canonical_source')),
        record('src/bhsm/interface/muon_magnetic_retarded_lepton.py',('reached_lorentz_magnetic_vertices','retarded_magnetic_lepton_application')),
        record('src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',('primal_trace_enriched_lepton_operator',)),
        record('scripts/evaluate_muon_magnetic_retarded_operators.py',('evaluate',))]
    for item in sources:hashes[item['path']]=item['sha256']
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('consumed owner changed')
    return serial(dict(classification='EVALUATED_TWO_TIME_REACHED_ACTION_GREEN_AND_OPEN_LEPTON_MAGNETIC_APPLICATIONS',
        input_hashes=hashes,source_records=sources,applications=rows,array_records={k:array_record(v) for k,v in arrays.items()},
        actual_source_two_channel_replay_relative_difference=replay_relative,
        classical_Green_equation='xdot=M^-1(p-B^T x)+v_b b+v_bdot bdot; pdot=B xdot+Kx+K_ib b+B_ib bdot',
        actual_open_lepton_equation='dU0/dt=-i N Hcan U0; ddeltaUn/dt=-i N Hcan,n deltaUn-i N deltaHcan,n0 U0',
        actual_vertex_equation='deltaHcan=-i alpha_i G_c deltaAi/R4-i G_c deltaAt/N+M_fixedY(deltaH)',
        next_open_loop_application='Sigma(x,y)=-V_A(x) G_F(x,y) V_B(y) deltaD_AB(x,y); magnetic variation includes both vertices, deltaG_F=-G_F deltaD_F G_F, and delta(deltaD)',
        quantum_covariance_consumed=False,
        precise_quantum_consumer_scope='retarded classical Euler/Gauss inverse and retarded fermion source do not determine the Feynman/Keldysh photon/fermion contraction; native positive P_A/ghost/HS relative domain or matched quantum spectral kernel must supply that contraction',
        three_axis_boundary_path_inverse_used_as_virtual_photon=False,
        time_translation_or_static_Fourier_background_assumed=False,
        lepton_arm_kernel_initial_identity_is_computational_basis_not_state=True,
        full_fermion_birth_bundle_reset_not_inferred_from_bosonic_pointwise_graph=True,
        native_positive_relative_heat_or_external_LSZ_Pauli_completed=False,complete_observable=False,
        error_scope='actual finite interpolated action coefficient core, saved source fields, retarded numerical integration and independent source-channel replay; not quantum covariance, continuum/native domain or soft observable enclosure')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--incoming-response',type=Path,required=True);p.add_argument('--outgoing-response',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate(dict(incoming=a.incoming_response,outgoing=a.outgoing_response));data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('preserve complete arrays by lossless split')
    a.output.mkdir(parents=True);(a.output/'application.npz').write_bytes(data)
    packet['archive']=dict(path='application.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'result.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],applications=packet['applications'],source_channel_replay_relative=replay_relative if False else packet['actual_source_two_channel_replay_relative_difference'])),flush=True)


if __name__=='__main__':main()
