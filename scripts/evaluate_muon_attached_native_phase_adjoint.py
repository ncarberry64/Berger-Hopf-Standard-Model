"""Contract executed full mean loads with same-cell native heat adjoints on the attached full-field base."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.muon_primal_native_phase_adjoint import (
    contract_phase_native_target,chronological_native_phase_jacobian,
)
from bhsm.interface.muon_primal_cell_native_heat import actual_cell_heat_polynomial,actual_cell_even_y_target
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(mean_directory,output):
    mean=Path(mean_directory);mean=mean if mean.is_absolute() else ROOT/mean
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier action applications')
    md=json.loads((mean/'mean_load.json').read_text(encoding='utf8'))
    if md['classification']!='EVALUATED_TOTAL_RAW268_CUBIC_MEAN_LOAD_FROM_FRESH_SAME_PHASE_RESPONSES':
        raise ValueError('executed complete same-phase raw268 mean load required')
    if sha256((mean/'mean_load.npz').read_bytes()).hexdigest()!=md['archive']['sha256']:
        raise ValueError('executed action load archive changed')
    hashes=dict(md['input_hashes'])
    own=[ROOT/'src/bhsm/interface/muon_primal_native_phase_adjoint.py',Path(__file__),
        ROOT/'src/bhsm/interface/muon_primal_cell_native_heat.py',
        ROOT/'src/bhsm/interface/muon_trace_enriched_charged_current_response.py',
        mean/'mean_load.json',mean/'mean_load.npz']
    hashes.update({p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in own})
    with np.load(mean/'mean_load.npz',allow_pickle=False) as f:loads={k:f[k].copy() for k in f.files}
    bound=[]
    for side in ('incoming','outgoing'):
        folder=ROOT/'artifacts/muon_parent_gauge_geometry_correction_20261010'/f'attached_phase_{side}_1steps_run_1'
        phase=json.loads((folder/'result.json').read_text(encoding='utf8'))
        if phase['side']!=side or phase['steps']!=1 or phase['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
            raise ValueError('the consumed complete one-cell phase must agree')
        for p in (folder/'result.json',folder/'application.npz'):
            name=p.relative_to(ROOT).as_posix()
            if name not in hashes or sha256(p.read_bytes()).hexdigest()!=hashes[name]:
                raise ValueError('mean load and adjoint must consume identical phase: '+name)
        if sha256((folder/'application.npz').read_bytes()).hexdigest()!=phase['numerical_sha256']:
            raise ValueError('phase archive changed')
        loaded=load_attached_endpoint(phase['consumed_paired_endpoint_path'],side=side)
        rep=loaded['representation']
        with np.load(folder/'application.npz',allow_pickle=False) as f:
            J=f['stage_jacobian'][0];raw=f['stage_midpoint_raw'][0]
        reached_raw=loads[side+'_raw268']
        bridge_difference=float(np.linalg.norm(raw-reached_raw))
        if bridge_difference>2e-13:raise ValueError('first response and target use different primal midpoints')
        # Retain the actual bridge values used in the executed mean load.
        polynomial=actual_cell_heat_polynomial(reached_raw,rep,length=abs(phase['span']))
        chronological=chronological_native_phase_jacobian(J,rep,phase['span'])
        bound.append((side,rep,phase,polynomial,chronological,bridge_difference))
    common_gap=min(float(np.linalg.eigvalsh(p['P0'])[0]) for _,_,_,p,_,_ in bound)
    arrays={};rows=[]
    for side,rep,phase,polynomial,chronological,difference in bound:
        print(json.dumps(dict(stage='actual_native_target_mean_adjoint',side=side)),flush=True)
        applications=[];load=loads[side+'_raw_mean_cotangent']
        if load.shape!=(268,8,8):raise ValueError('all ordered reached source pairs required')
        arrays[side+'_raw_mean_cotangent']=load
        arrays[side+'_chronological_J']=chronological['jacobian']
        for q in (.25,1.,4.):
            c=q/common_gap;target=actual_cell_even_y_target(polynomial,c)
            gradient=target['paired_middle_minus_light_raw_cotangent'];frames=[]
            for frame in ('temporal','radial'):
                a=contract_phase_native_target(chronological['jacobian'],rep,chronological['step'],gradient,load,frame=frame)
                label=side+'_q_'+str(q).replace('.','p')+'_'+frame
                for name,value in a.items():
                    if isinstance(value,np.ndarray):arrays[label+'_'+name]=value
                arrays[label+'_raw_target']=gradient
                keys=('bordered_adjoint_residual_norm','scaled_bordered_adjoint_residual_norm',
                    'original_adjoint_defect_norm','auxiliary_Gauss_reaction_norm','balanced_condition_number')
                frames.append(dict(frame=frame,checks={k:a[k] for k in keys},
                    native_mean_response_norm=float(np.linalg.norm(a['native_mean_response_pair'])),
                    native_mean_response_trace=float(np.trace(a['native_mean_response_pair'])),
                    native_mean_response_pair=a['native_mean_response_pair'].tolist(),
                    target_frame_contact_norm=float(np.linalg.norm(a['target_frame_contact'])),
                    source_pair_symmetry_defect=float(np.linalg.norm(a['native_mean_response_pair']-a['native_mean_response_pair'].T))))
            frame_difference=float(np.linalg.norm(np.array(frames[0]['native_mean_response_pair'])-np.array(frames[1]['native_mean_response_pair'])))
            applications.append(dict(q_probe=q,cutoff_probe=c,frames=frames,named_frame_pair_difference=frame_difference,
                source_pair_scope='actual compact-pulse first response at midpoint, complete raw268 cubic load and native homogeneous target; direct first-field heat sector handled separately'))
        rows.append(dict(side=side,stored_phase_span=phase['span'],chronological_step=chronological['step'],
            incoming_response_time_direction_reversed=chronological['incoming_time_direction_reversed'],
            phase_to_source_bridge_raw_difference=difference,
            action_parameters=phase['action_parameters'],applications=applications))
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:
        raise RuntimeError('consumed action or response changed during contraction')
    out.mkdir(parents=True);archive=out/'application.npz';deterministic_archive(archive,arrays)
    if archive.stat().st_size>10*1024**2:raise ValueError('complete arrays require lossless split')
    result=dict(classification='EVALUATED_CHRONOLOGICAL_NATIVE_TARGET_ADJOINT_ON_ACTUAL_CUBIC_MEAN_LOAD',
        input_hashes=hashes,array_archive=dict(path=archive.name,sha256=sha256(archive.read_bytes()).hexdigest(),bytes=archive.stat().st_size),
        common_gap_probe=common_gap,arms=rows,
        action_response_equation='J delta=-F; G=dGamma/draw*raw_from_phase; K^T p=(G,0); response=-p_original^T F',
        mean_load_from_executed_same_phase_first_fields=True,
        complete358_Euler_Legendre_Gauss_multiplier_rows_retained=True,
        auxiliary_Gauss_reactions_and_target_frame_contacts_retained=True,
        boundary_policy='initial chronological phase response held; two named central frame conditions; no artificial shared birth dual',
        incoming_field_rate_sign_reversed=False,instantaneous_Legendre_inverse_or_pseudoinverse_used=False,
        repeated_source_pair_factor_of_two_applied=False,
        direct_first_field_heat_insertions_included=False,
        no_physical_cutoff_or_relative_native_or_overlap_completion_claimed=True,
        action_selected=False,Gate7_closed=False,complete_observable=False,
        error_scope='binary64 complete saved phase system and literal weak loads; paired heatY2 target on normalized finite Dirichlet cell; no spatial/temporal continuum, physical Pauli or anomaly bound')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return {k:result[k] for k in ('classification','array_archive','arms')}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mean-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.mean_directory,a.output),sort_keys=True))
