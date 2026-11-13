"""Combine actual magnetic direct/mean terms with the verified mean intervals."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import serial,record,array_record,deterministic_npz
from bhsm.interface.muon_magnetic_native_source_pair import combine_magnetic_direct_and_verified_mean,magnetic_finite_core_overlap_moment
from bhsm.interface.muon_magnetic_source_mean_load import load_magnetic_reached_mean_inputs,magnetic_reached_first_fields
from bhsm.interface.muon_magnetic_cell_source_heat import magnetic_source_heat_polynomial
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space


def _load(directory,json_name,archive_field,hashes):
    folder=Path(directory);folder=folder if folder.is_absolute() else ROOT/folder
    raw=(folder/json_name).read_bytes();packet=json.loads(raw)
    for name,digest in packet['input_hashes'].items():
        if name in hashes and hashes[name]!=digest:raise ValueError('same action owner differs: '+name)
        hashes[name]=digest
    hashes[(folder/json_name).relative_to(ROOT).as_posix()]=sha256(raw).hexdigest()
    info=packet[archive_field];data=(folder/info['path']).read_bytes()
    if len(data)!=info['bytes'] or sha256(data).hexdigest()!=info['sha256']:raise ValueError('consumed archive changed')
    hashes[(folder/info['path']).relative_to(ROOT).as_posix()]=info['sha256']
    with np.load(folder/info['path'],allow_pickle=False) as f:arrays={k:f[k].copy() for k in f.files}
    return packet,arrays


def _arrays(value,prefix,output):
    if isinstance(value,np.ndarray):output[prefix]=value
    elif isinstance(value,dict):
        for name,child in value.items():_arrays(child,prefix+'_'+name,output)


def evaluate(direct_directory,mean_directory,certificate_directory,directories):
    hashes={};direct,D=_load(direct_directory,'source_heat.json','archive',hashes)
    mean,M=_load(mean_directory,'result.json','array_archive',hashes)
    certificate,C=_load(certificate_directory,'result.json','archive',hashes)
    if direct['classification']!='EVALUATED_ACTIVE_MAGNETIC_GAUGE_PLUS_H_SAME_CELL_HEAT_SOURCE_PAIR':raise ValueError('actual active magnetic direct pair required')
    if mean['classification']!='EVALUATED_CHRONOLOGICAL_NATIVE_TARGET_ADJOINT_ON_ACTUAL_CUBIC_MEAN_LOAD':raise ValueError('complete per-arm native mean adjoint required')
    if direct['common_zero_Y_gap']!=mean['common_gap_probe']:raise ValueError('direct and mean cutoff normalization differs')
    angular=retained_full_q_angular_space(ROOT);arrays={};arms=[]
    for side,directory in directories.items():
        inputs=load_magnetic_reached_mean_inputs(directory,repository=ROOT)
        for name,digest in inputs['input_hashes'].items():
            if name in hashes and hashes[name]!=digest:raise ValueError('direct/mean source owner differs')
            hashes[name]=digest
        fields=magnetic_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
        if not np.array_equal(fields['raw_fields'],D[side+'_raw_fields']):raise ValueError('direct uses a different actual coefficient cell')
        arm=next(a for a in direct['arms'] if a['side']==side);rows=[]
        for j,sample in enumerate(arm['applications']):
            q=sample['q_probe'];prefix=side+'_q_'+str(q).replace('.','p');frames=[]
            pieces={name:D[prefix+'_paired_middle_minus_light_Y2_source_pair_'+name] for name in
                ('source_square_contact','ordered_two_insertion','opposite_order_two_insertion')}
            for frame in ('temporal','radial'):
                proof=next(a for a in certificate['applications'] if a['side']==side and a['frame']==frame)
                if proof['q_probes'][j]!=q:raise ValueError('certified native target ordering differs')
                lo=np.asarray(proof['contraction_lower'][j]);hi=np.asarray(proof['contraction_upper'][j])
                result=combine_magnetic_direct_and_verified_mean(pieces,lo,hi);label=prefix+'_'+frame
                _arrays(result,label,arrays)
                binary=M[label+'_native_mean_response_pair']
                arrays[label+'_original_binary_mean']=binary
                frames.append(dict(frame=frame,graded_trace=float(np.trace(result['graded_source_pair']).real),
                    graded_source_pair=serial(result['graded_source_pair']),
                    exact_stored_mean_plus_stored_direct_real_lower=serial(result['graded_exact_stored_mean_plus_stored_direct_real_lower']),
                    exact_stored_mean_plus_stored_direct_real_upper=serial(result['graded_exact_stored_mean_plus_stored_direct_real_upper']),
                    binary_vs_exact_mean_maximum=float(np.max(abs(binary-(lo+(hi-lo)/2)))),
                    direct_contour_lag_refinement_absolute=sample['contour_lag_refinement_absolute'],
                    paired_even_Y4_majorant_estimate_maximum=sample['paired_even_Y4_majorant_estimate_maximum'],
                    source_pair_statistics_factor=.5,
                    induced_mean_scope=result['induced_mean_scope']))
            rows.append(dict(q_probe=q,cutoff_probe=sample['cutoff_probe'],frames=frames))
        poly=magnetic_source_heat_polynomial(fields,inputs['representation'],angular,length=inputs['times'][-1])
        moments=[]
        for frame in ('temporal','radial'):
            overlap=magnetic_finite_core_overlap_moment(fields,inputs['representation'],poly,
                M[side+'_raw_mean_cotangent'],M[side+'_chronological_J'],inputs['times'][-1],
                length=inputs['times'][-1],frame=frame)
            _arrays(overlap,side+'_finite_core_overlap_'+frame,arrays)
            moments.append(dict(frame=frame,paired_TrP_direct_trace=float(np.trace(overlap['paired_TrP_Y2_direct_contact']).real),
                paired_TrP_mean_trace=float(np.trace(overlap['paired_TrP_Y2_mean_contact']).real),
                finite_moment_subtracted=False,full_continuum_local_overlap_inferred=False))
        arms.append(dict(side=side,applications=rows,finite_core_overlap_applications=moments,
            active_source_indices=[0,1,2],inactive_padded_source_indices=[3,4,5,6,7],
            source_profile=fields['profile'],source_profile_rate=fields['profile_rate']))
    sources=[record('src/bhsm/interface/muon_magnetic_native_source_pair.py',('combine_magnetic_direct_and_verified_mean','magnetic_finite_core_overlap_moment')),
        record('src/bhsm/interface/muon_attached_native_source_pair.py',('combine_executed_fermion_pair',)),
        record('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',('microscopic_owner_contract',)),
        record('scripts/evaluate_muon_magnetic_native_source_pair.py',('evaluate',))]
    for item in sources:hashes[item['path']]=item['sha256']
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('consumed source or action changed')
    return serial(dict(classification='EVALUATED_SAME_LOCAL_MAGNETIC_CELL_GRADED_DIRECT_PLUS_VERIFIED_MEAN_FERMION_SOURCE_PAIR',
        input_hashes=hashes,source_records=sources,arms=arms,array_records={k:array_record(v) for k,v in arrays.items()},
        fermion_statistics_factor=.5,statistics_owner='Gamma=-STr E1/2; complex Grassmann gives +Tr E1/2',
        no_charge_conjugate_or_Nambu_doubling=True,direct_contact_and_both_ordered_insertions_retained=True,
        all_represented_358_mean_rows_reactions_retained=True,common_birth_second_mean_transfer_completed=False,
        first_source_common_birth_state_transferred=True,
        finite_core_overlap_moment_evaluated_but_not_subtracted=True,
        open_one_loop_scalar_H1_overlap_zero_by_source_leg_topology=True,
        continuum_QED_VP_overlap_requires_same_loop_current_momentum_and_domain=True,
        full_bosonic_A0_blindly_subtracted=False,induced_disjoint_native_label_justified=False,
        physical_cutoff_domain_relative_eta_ghost_LSZ_or_Pauli_completed=False,complete_observable=False,
        error_scope='stored mean interval certification plus stored direct entries; binary mean discrepancy preserved; separate direct contour/lag and conditional Y4 estimates exclude upstream assembly, source/time, physical domain/cutoff, second-mean reset and soft-loop matching errors')),arrays


def main():
    p=argparse.ArgumentParser()
    for name in ('direct-directory','mean-directory','certificate-directory','incoming-response','outgoing-response','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate(a.direct_directory,a.mean_directory,a.certificate_directory,
        dict(incoming=a.incoming_response,outgoing=a.outgoing_response))
    data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('preserve complete arrays with lossless split')
    a.output.mkdir(parents=True);(a.output/'source_pair.npz').write_bytes(data)
    packet['archive']=dict(path='source_pair.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'source_pair.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],traces=[
        dict(side=arm['side'],values=[(a['q_probe'],f['graded_trace']) for a in arm['applications'] for f in a['frames'] if f['frame']=='temporal']) for arm in packet['arms']])),flush=True)


if __name__=='__main__':main()
