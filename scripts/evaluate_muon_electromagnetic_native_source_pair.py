"""Apply actual H-selected electromagnetic contact, both insertions and mean."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate_muon_native_product_factor_graph import record,serial,array_record,deterministic_npz
from bhsm.interface.muon_electromagnetic_source_mean_load import load_electromagnetic_reached_mean_inputs
from bhsm.interface.muon_current_source_motion_mean_load import enriched_reached_first_fields
from bhsm.interface.muon_attached_native_source_pair import attached_same_cell_source_pair,actual_finite_core_overlap_moment
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_primal_native_phase_adjoint import chronological_native_phase_jacobian


def _arrays(value,prefix,output):
    if isinstance(value,np.ndarray):output[prefix]=value
    elif isinstance(value,dict):
        for name,child in value.items():_arrays(child,prefix+'_'+name,output)


def evaluate(directories,mean_directory):
    mean=Path(mean_directory);mean=mean if mean.is_absolute() else ROOT/mean
    data=(mean/'result.json').read_bytes();md=json.loads(data)
    if md['classification']!='EVALUATED_CHRONOLOGICAL_NATIVE_TARGET_ADJOINT_ON_ACTUAL_CUBIC_MEAN_LOAD':
        raise ValueError('executed chronological complete mean target required')
    hashes=dict(md['input_hashes']);hashes[(mean/'result.json').relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    data=(mean/md['array_archive']['path']).read_bytes()
    if len(data)!=md['array_archive']['bytes'] or sha256(data).hexdigest()!=md['array_archive']['sha256']:
        raise ValueError('executed mean target changed')
    hashes[(mean/md['array_archive']['path']).relative_to(ROOT).as_posix()]=sha256(data).hexdigest()
    for name,digest in hashes.items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise ValueError('consumed mean owner changed: '+name)
    with np.load(mean/md['array_archive']['path'],allow_pickle=False) as f:mean_arrays={k:f[k].copy() for k in f.files}
    angular=retained_full_q_angular_space(ROOT);arrays={};rows=[]
    for side,directory in directories.items():
        print(json.dumps(dict(stage='same_attached_background_contact_both_insertions_mean_overlap',side=side)),flush=True)
        inputs=load_electromagnetic_reached_mean_inputs(directory,repository=ROOT)
        if inputs['receipt']['side']!=side:raise ValueError('response arm mismatch')
        for name,digest in inputs['input_hashes'].items():
            if name in hashes and hashes[name]!=digest:raise ValueError('direct and mean owner differ: '+name)
            hashes[name]=digest
        phase_folder=inputs['actual_attached_phase_path']
        for name in ('result.json','application.npz'):
            rel=(phase_folder/name).relative_to(ROOT).as_posix()
            if rel not in md['input_hashes'] or md['input_hashes'][rel]!=sha256((phase_folder/name).read_bytes()).hexdigest():
                raise ValueError('direct and mean must bind the SAME attached phase')
        fields=enriched_reached_first_fields(inputs,inputs['times'][len(inputs['times'])//2])
        # Root exports precisely the raw midpoint used by its mean target.
        expected_raw=mean_arrays[side+'_raw_mean_cotangent']
        if expected_raw.shape!=(268,8,8):raise ValueError('complete reached mean load required')
        with np.load(phase_folder/'application.npz',allow_pickle=False) as f:J=f['stage_jacobian'][0].copy()
        chronological=chronological_native_phase_jacobian(J,inputs['representation'],inputs['receipt']['actual_phase_span'])
        if not np.array_equal(chronological['jacobian'],mean_arrays[side+'_chronological_J']):
            raise ValueError('direct overlap and mean adjoint use different chronological rows')
        arm=next(a for a in md['arms'] if a['side']==side);applications=[]
        for sample in arm['applications']:
            q=sample['q_probe'];c=sample['cutoff_probe'];frames=[]
            for frame in ('temporal','radial'):
                label=side+'_q_'+str(q).replace('.','p')+'_'+frame
                result=attached_same_cell_source_pair(inputs,angular,
                    mean_arrays[label+'_native_mean_response_pair'],cutoff=c)
                for name,value in result['combined'].items():
                    if isinstance(value,np.ndarray):arrays[label+'_'+name]=value
                if frame=='temporal':
                    direct=result['direct_application']
                    for name,value in direct['paired_middle_minus_light_Y2_source_pair'].items():
                        arrays[side+'_q_'+str(q).replace('.','p')+'_direct_'+name]=value
                    if q==arm['applications'][0]['q_probe']:
                        _arrays(direct['zero_Y_source_core'],side+'_zero_Y_source_core',arrays)
                        arrays[side+'_raw268']=fields['raw_fields'];arrays[side+'_first_H']=fields['first_H']
                        arrays[side+'_first_H_rate']=fields['first_H_rate'];arrays[side+'_first_wall_gauge']=fields['first_wall_gauge']
                frames.append(dict(frame=frame,graded_source_pair=serial(result['combined']['graded_source_pair']),
                    graded_trace=float(np.trace(result['combined']['graded_source_pair']).real),
                    graded_norm=float(np.linalg.norm(result['combined']['graded_source_pair'])),
                    direct_trace=direct['paired_middle_minus_light_Y2_channel_trace'],
                    mean_trace=float(np.trace(mean_arrays[label+'_native_mean_response_pair'])),
                    source_symmetry_defect=float(np.linalg.norm(result['combined']['graded_source_pair']-result['combined']['graded_source_pair'].T)),
                    paired_direct_lag_rule32_64_estimate=direct['paired_middle_minus_light_lag_rule32_64_difference_norm'],
                    mean_checks=next(f['checks'] for f in sample['frames'] if f['frame']==frame)))
            applications.append(dict(q_probe=q,cutoff_probe=c,frames=frames))
        overlaps=[]
        for frame in ('temporal','radial'):
            overlap=actual_finite_core_overlap_moment(fields,inputs['representation'],angular,expected_raw,
                chronological['jacobian'],chronological['step'],length=abs(inputs['receipt']['actual_phase_span']),frame=frame)
            _arrays(overlap,side+'_finite_core_overlap_'+frame,arrays)
            overlaps.append(dict(frame=frame,
                common_family_central_mixed_overlap='exact zero for identical Y0 family coefficient/source/domain/mean path only',
                paired_TrP_Y2_direct_trace=float(np.trace(overlap['paired_TrP_Y2_direct_contact']).real),
                paired_TrP_Y2_mean_trace=float(np.trace(overlap['paired_TrP_Y2_mean_contact']).real),
                paired_TrP_Y2_complete_trace=float(np.trace(overlap['paired_TrP_Y2_complete_contact']).real),
                paired_first_short_heat_coefficient_trace=float(np.trace(overlap['paired_first_short_heat_coefficient']).real),
                actual_mass_dependent_coefficient_norm=float(np.linalg.norm(overlap['paired_TrP_Y2_complete_contact'])),
                finite_core_coefficient_subtracted=False,continuum_local_coefficient_inferred=False))
        rows.append(dict(side=side,coordinate_time=fields['coordinate_time'],response_time=fields['response_time'],
            source_profile=fields['profile'],source_profile_rate=fields['profile_rate'],applications=applications,
            overlap_applications=overlaps,source_direction_order='eight actual Higgs-selected EM coexact wavefunctions in full400; no external momentum or fermion Hessian direction',
            source_normalization='beta=Tb(current R4) S(H_base) b; geometric and charge-direction rate composed before Gauss; no extra e, QNORM or Haar volume',
            preserved_mean_reactions=True,all64_ordered_pairs_retained=True))
    sources=[record('src/bhsm/interface/muon_attached_native_source_pair.py',
        ('combine_executed_fermion_pair','actual_finite_core_overlap_moment','attached_same_cell_source_pair')),
        record('src/bhsm/interface/muon_electromagnetic_source_mean_load.py',('load_electromagnetic_reached_mean_inputs','electromagnetic_source_complete_mean_load')),
        record('src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',('microscopic_owner_contract','induced_local_weight_ledger')),
        record('src/bhsm/interface/muon_native_induced_polarization.py',('local_subtraction_component',)),
        record('scripts/evaluate_muon_electromagnetic_native_source_pair.py',('evaluate',))]
    for item in sources:hashes[item['path']]=item['sha256']
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:
        raise RuntimeError('consumed action or response changed')
    return serial(dict(classification='EVALUATED_SAME_ELECTROMAGNETIC_CELL_GRADED_DIRECT_PLUS_MEAN_FERMION_SOURCE_PAIR',
        input_hashes=hashes,source_records=sources,arms=rows,array_records={k:array_record(v) for k,v in arrays.items()},
        fermion_statistics_factor=.5,statistics_owner='Gamma=-STr E1/2; complex Grassmann fermion gives+Tr E1/2',
        charge_conjugate_realification_or_Nambu_doubling_used=False,source_pair_factor_of_two_applied=False,
        contact_and_both_ordered_insertions_and_mean_operator_contact_included=True,
        common_family_central_overlap_cancelled=True,
        common_family_central_cancellation_scope='identical Y0 coefficient/source/domain/mean map on the two C6 family copies; no inference for external-mass-dependent Pauli matching',
        mass_dependent_finite_local_moment_evaluated=True,full_continuum_overlap_subtraction_applied=False,
        full_bosonic_A0_subtracted_from_partial_fermion_trace=False,
        local_heat_owner_scope='M8/M5/M4 local actions are expansions of one microscopic functional; finite n0 trace is not the full continuum heat coefficient',
        induced_disjoint_native_label_justified=False,
        determinant_phase_relative_eta_evaluated=False,physical_birth_cutoff_selected=False,
        actual_H_selected_EM_source_used=True,old_transported_Q8_source_substituted=False,
        source_prescription='background-bound linear electromagnetic probe with Q_H(H_base(t)); base homogeneous H/geometry source jets retained',
        full_angular_field_dependent_charge_source_family_claimed=False,
        nonlinear_angular_H_axis_source_contacts_included=False,
        nonlinear_axis_second_wall_contact_zero_midpoint_scope='pulse value and rate zero outside support; no claim for active-pulse history',
        external_fermion_Hessian_or_momentum_soft_derivative_present=False,
        complete_native_ghost_strong_LSZ_or_Pauli=False,action_selected=False,Gate7_closed=False,complete_observable=False,
        error_scope='actual binary64 Y2 direct and chronological mean applications;64point lag refinement estimate, exact stored mean certificate separate; Y4/continuum/domain/cutoff/relative eta/local overlap/soft readout not assigned an error bound')),arrays


def main():
    p=argparse.ArgumentParser();p.add_argument('--incoming-response',type=Path,required=True);p.add_argument('--outgoing-response',type=Path,required=True)
    p.add_argument('--mean-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('preserve earlier applications')
    packet,arrays=evaluate(dict(incoming=a.incoming_response,outgoing=a.outgoing_response),a.mean_directory)
    data=deterministic_npz(arrays)
    if len(data)>10*1024**2:raise ValueError('retain complete arrays by a lossless split')
    a.output.mkdir(parents=True);(a.output/'source_pair.npz').write_bytes(data)
    packet['archive']=dict(path='source_pair.npz',bytes=len(data),sha256=sha256(data).hexdigest())
    raw=(json.dumps(packet,indent=2,sort_keys=True,allow_nan=False)+'\n').encode();(a.output/'source_pair.json').write_bytes(raw)
    print(json.dumps(dict(receipt_sha256=sha256(raw).hexdigest(),archive=packet['archive'],
        applications=[dict(side=arm['side'],graded_traces=[dict(q_probe=s['q_probe'],cutoff_probe=s['cutoff_probe'],
            temporal=f['graded_trace']) for s in arm['applications'] for f in s['frames'] if f['frame']=='temporal'],
            overlap_applications=arm['overlap_applications']) for arm in packet['arms']])),flush=True)


if __name__=='__main__':main()
