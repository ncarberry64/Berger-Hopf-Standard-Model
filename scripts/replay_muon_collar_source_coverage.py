"""Focused continuation from bddd4e68; no old production/replay is run."""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):p.write_bytes((json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def git(root,*args):
    return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false','-C',str(root),*args],text=True)
def read_npz(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def prefix_duration(root):
    """Sum the existing chosen 1222-segment chronology, not alternative covers.

    No historic proof is rerun. Sum exact binary64 endpoints as Fractions and
    round outward. The inherited error/center scope is not strengthened.
    """
    base=root/'artifacts/flagship_integration';records=[];paths=[]
    def record(name):
        p=base/(name+'.json');paths.append(p);return json.loads(p.read_text())
    def add(name,lohi,count,start,end):
        records.append(dict(producer=name,interval=lohi,segments=count,start=start,end=end))
    name='BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION';j=record(name)
    add(name,j['extended_segment']['proper_time_interval'],1,0,1)
    name='BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT';j=record(name)
    add(name,j['translated_segment']['proper_time_increment_interval'],1,1,2)
    name='BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT';j=record(name)
    rows=j['cover']['rows'];ends=[sum((Fraction(float(r['proper_time_increment_interval'][i])) for r in rows),Fraction()) for i in range(2)]
    add(name,[float(np.nextafter(float(ends[0]),-np.inf)),float(np.nextafter(float(ends[1]),np.inf))],len(rows),2,436)
    for name,key in [
        ('BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION','compensated_cover'),
        ('BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION','adaptive_cover'),
        ('BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION','recentered_cover'),
        ('BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION','continuation'),
        ('BHSM_N12_C2_UNIFORM_GAP_CONTINUATION','continuation'),
        ('BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION','continuation')]:
        j=record(name)[key];n=j['additional_certified_segments'];a=j['prior_total_segments']
        add(name,j['additional_proper_duration_interval'],n,a,a+n)
    for n in range(1215,1223):
        name='BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP' if n==1215 else f'BHSM_N12_C2_LOHNER_STEP_{n}'
        j=record(name)['segment'];add(name,j['proper_time_increment_interval'],1,n-1,n)
    for previous,current in zip(records,records[1:]):
        if previous['end']!=current['start']:raise ValueError('prefix chronology gap; no invented duration')
    total=[sum((Fraction(float(r['interval'][i])) for r in records),Fraction()) for i in range(2)]
    return dict(records=records,proper_duration_interval=[float(np.nextafter(float(total[0]),-np.inf)),float(np.nextafter(float(total[1]),np.inf))],
        total_segments=1222,tail_clock_origin='proper time zero at inherited C2 step1222 frontier',
        reset_in_tail_clock_interval=[-float(np.nextafter(float(total[1]),np.inf)),-float(np.nextafter(float(total[0]),-np.inf))],
        physical_prefix_reintegrated=False,prefix_metric_continuation_evaluated=False,
        inherited_scope='previous certified duration intervals; proof-center metric data are not a new continuum collar certificate'),paths


def prefix_coefficients(root,geometry):
    """Materialize only the retained prefix, with no new trajectory solve."""
    from bhsm.interface.muon_parent_maxwell_velocity import current_parent_fields
    from bhsm.interface.aether_forward_boundary_radius import boundary_log_radius
    base=root/'artifacts/flagship_integration';paths=[];states=[];junctions=[]
    def load(name):
        p=base/(name+'.npz');paths.append(p);return read_npz(p)
    outer=load('BHSM_N12_C2_POLE_FREE_OUTER_MARGIN_EXTENSION')
    states.extend([outer['refined_C2_center'],outer['C2_predictor_state']])
    states.append(load('BHSM_N12_C2_TRANSLATED_POLE_FREE_SEGMENT')['C2_predictor_state'])
    groups=[('BHSM_N12_C2_EXTENDED_DESCRIPTOR_RESOLUTION_AUDIT','C2_predictor_centers'),
        ('BHSM_N12_C2_COMPENSATED_DESCRIPTOR_CONTINUATION','C2_compensated_predictor_centers'),
        ('BHSM_N12_C2_ADAPTIVE_BALL_CONTINUATION','C2_adaptive_predictor_centers'),
        ('BHSM_N12_C2_RECENTERED_ADAPTIVE_CONTINUATION','C2_recentered_adaptive_predictor_centers'),
        ('BHSM_N12_C2_DESCRIPTOR_FIBER_CANCELLED_CONTINUATION','C2_descriptor_fiber_predictor_centers'),
        ('BHSM_N12_C2_UNIFORM_GAP_CONTINUATION','C2_uniform_gap_predictor_centers'),
        ('BHSM_N12_C2_SECOND_UNIFORM_GAP_CONTINUATION','C2_second_uniform_gap_predictor_centers')]
    for name,key in groups:
        a=load(name)
        mismatch=float(np.linalg.norm((a[key][0]-states[-1])*a['state_weights']))
        junctions.append(dict(producer=name,weighted_center_recenter_difference=mismatch,
            interpretation='proof-center recentering; not a new physical metric discontinuity'))
        # Preserve both sides in the enclosing coefficient hull if recentered.
        states.append(a[key][0]);states.extend(a[key][1:])
    for n in range(1215,1223):
        name='BHSM_N12_C2_CANCELLED_FIELD_LOHNER_STEP' if n==1215 else f'BHSM_N12_C2_LOHNER_STEP_{n}'
        a=load(name);states.append(a['center_state']);states.append(a['endpoint_predictor_center'])
    states=np.array(states)
    logR=np.array([boundary_log_radius(12,q[:37]) for q in states])
    fields=current_parent_fields(states,logR,geometry['rho'])
    Tb=(2*np.pi**2*np.exp(logR))**-.5
    fields['continued_T_b']=Tb
    mismatch={k:float(np.max(abs(fields[k][-1]-geometry[k][0]))) for k in
        ('proper_lapse','C_rho','proper_shift_rho','base_radius')}
    return fields,dict(prefix_center_count=len(states),history_segments=1222,
        attachment='boundary_log_radius -> current_parent_fields; same current q_W attachment, not copied RADIUS0',
        tail_join_maximum_absolute_difference=mismatch,recenter_junctions=junctions,
        actual_production_solve_count=0,source='same beta=T_b b coefficient, same Q and saved rho hat; no new continuation profile'),paths


def run(root,out,resume=None):
    if out.exists():raise FileExistsError('fresh output directory required')
    out.mkdir(parents=True);started=time.perf_counter()
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_collar_source_coverage import continue_saved_collar,spin_transport,prefix_coverage_enclosure
    refs=dict(
      metric=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
      saved_curve=root/'artifacts/muon_eta_profile_attachment_20261003/replay_reference/daughter_collar_profile.npz',
      source_pairing=root/'artifacts/muon_wall_source_pairing_20261003/replay_reference/source_reached_pairings.npz',
      corrected_source=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/parent_source_rate_corrected.npz',
      cut_rate=root/'artifacts/muon_parent_source_rate_20261003/replay_reference/cut_rate_record.json',
      frozen_local=root/'artifacts/muon_eta_profile_attachment_20261003/replay_reference/frozen_local.json',
      native_ledger=root/'artifacts/muon_eta_profile_attachment_20261003/replay_reference/native_ledger.json')
    chronology,paths=prefix_duration(root)
    refs.update({f'prefix_{i}':p for i,p in enumerate(paths)})
    refs.update(module=root/'src/bhsm/interface/muon_collar_source_coverage.py',script=Path(__file__),
        parent_field_producer=root/'src/bhsm/interface/muon_parent_maxwell_velocity.py',
        radius_producer=root/'src/bhsm/interface/aether_forward_boundary_radius.py')
    if resume:
        refs.update(resumed_collar=resume/'collar_coverage_actions.npz',resumed_result=resume/'result.json')
    identities={k:dict(path=str(p.relative_to(root)) if p.is_relative_to(root) else str(p),sha256=digest(p)) for k,p in refs.items()}
    save(out/'input_hashes.json',identities)
    save(out/'prefix_chronology.json',chronology)
    save(out/'workspace.json',dict(branch=git(root,'branch','--show-current').strip(),head=git(root,'rev-parse','HEAD').strip(),
         reference='524ed90689bd5923c249bba2e699abf627e703cd',starting_checkpoint='bddd4e68ebc6b84efab29c051c5df4c53ba727c6',
         status=git(root,'status','--short')))
    (out/'working_tree.diff').write_bytes(git(root,'diff','--binary').encode())
    save(out/'stage.json',dict(stage='inputs recorded; starting only new collar actions',old_productions_rerun=False))
    geometry=read_npz(refs['metric']);old=read_npz(refs['saved_curve']);pairing=read_npz(refs['source_pairing'])
    corrected=read_npz(refs['corrected_source'])
    if resume:
        arrays=read_npz(refs['resumed_collar']);result=json.loads(refs['resumed_result'].read_text())
        result['resumed_collar_actions']=dict(path=str(resume),sha256=digest(refs['resumed_collar']),new_phase_integrations=0)
    else:
        arrays,result=continue_saved_collar(geometry,old)
    transport,transport_result=spin_transport(arrays,corrected['parent_gamma'],corrected['gamma5'])
    arrays.update(transport)
    support=[float(geometry['rho'][int(min(pairing['gauss_cells']))]),float(geometry['rho'][int(max(pairing['gauss_cells']))+1])]
    reached=(arrays['rho']>=support[0])&(arrays['rho']<=support[1])
    if np.any(reached):raise RuntimeError('support reached; implement actual saved-integrand contraction instead of a coverage-only receipt')
    arrays['saved_source_support_envelope']=np.array(support)
    # Only the currently covered normal integral has zero compact-source part.
    # This is not the full overlap, B, or a claim about propagated source traces.
    arrays.pop('unnormalized_covered_source_T_n1',None);arrays.pop('unnormalized_covered_source_T_n3',None)
    prefix_fields,prefix_receipt,prefix_paths=prefix_coefficients(root,geometry)
    refs.update({f'prefix_states_{i}':p for i,p in enumerate(prefix_paths)})
    prefix_arrays,prefix_result=prefix_coverage_enclosure(geometry,prefix_fields,arrays,chronology['proper_duration_interval'][1])
    prefix_arrays['continued_T_b']=prefix_fields['continued_T_b']
    np.savez_compressed(out/'prefix_collar_enclosure.npz',**prefix_arrays)
    save(out/'prefix_collar_enclosure.json',prefix_result)
    save(out/'prefix_coefficient_receipt.json',prefix_receipt)
    prefix_error=prefix_result['radial_displacement_upper']['interval'][1]
    if not min(arrays['rho'])-prefix_error>support[1]:raise ArithmeticError('prefix enclosure does not exclude source support')
    identities={k:dict(path=str(p.relative_to(root)) if p.is_relative_to(root) else str(p),sha256=digest(p)) for k,p in refs.items()}
    save(out/'input_hashes.json',identities)
    np.savez_compressed(out/'collar_coverage_actions.npz',**arrays)
    result.update(spin_transport=transport_result,prefix_chronology=chronology,
        prefix_coefficient_receipt=prefix_receipt,prefix_collar_enclosure=prefix_result,
        saved_source_support=support,covered_source_support=False,
        covered_compact_source_integral='exactly zero on disjoint covered patch only; full required overlap remains unevaluated',
        nearest_radial_gap_to_source=float(min(arrays['rho'])-support[1]),
        T_required=None,B54_required=None,exterior_K_M=None,stationary_response=None,
        native_heat_contact=None,physical_a_mu=None,physical_g_mu=None,
        native_physical_transfer_directions=0,
        first_unresolved_operand=dict(
          name='inverse/patched collar action on the saved source-support points',
          equation='X(s_j,y_j)=(tau_cut=0,rho_j) for actual saved Gauss source points in the inherited domain; W=J^-1/2 sin(rho(X)/2) U54/sqrt(I); W^dagger M5 W=M4',
          input='resolved daughter eta field, current collar values, inherited E1 reset and source-support data; no new state/profile/arm',
          output='source-relevant overlap W_eta^sharp p across a justified domain/patch representation',
          producer='adopted v14.45 normalized inclusion and current normal/patch geometry; if the owned representation crosses E1 use AE2 Gamma0_child W_child T_R=U_R Gamma0_event W_event with its inherited wall-input map',
          consumer='saved compact-source T=<W_eta e,p>_5 then M4 B=T and coupled exterior K/M',
          status='uncomputed compatible source-restricted patch action; this Gaussian realization exits before support, not proof that reset crossing is the unique route or that another physical datum is required'),
        numerical_error=dict(ODE_absolute_bound=None,continuum_history_bound=None,
          cached_segment='explicit Hermite reconstruction, sampled geodesic defect recorded; no stability bound inferred',
          inherited_H='unchanged independent source-rate interval; not substituted for metric time derivatives',
          normalization_remainder=None,source_transport_pairing_domain_derivatives=None),
        old_phase_reintegrated=False,old_production_or_replay_count=0,elapsed_seconds=time.perf_counter()-started)
    save(out/'result.json',result)
    save(out/'checkpoint.json',dict(id='BHSM_MUON_COLLAR_PREFIX_COVERAGE_20261003',
        result='result.json',arrays='collar_coverage_actions.npz',next_operand=result['first_unresolved_operand'],
        resume_state=result['cache_exit_phase'],resume_variation=result['cache_exit_transverse'],resume_normal_s=result['cache_exit_s'],
        old_results_preserved=True,physical_prediction=False))
    save(out/'frozen_ledger.json',{k:json.loads(refs[k].read_text()) for k in ('frozen_local','native_ledger')})
    save(out/'output_hashes.json',{p.name:digest(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps({k:result[k] for k in ('cache_exit_s','cache_exit_phase','cache_exit_J','rho_range','minimum_abs_Delta','I_partial','saved_source_support','nearest_radial_gap_to_source','elapsed_seconds')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--resume-collar',type=Path)
    args=parser.parse_args();run(args.repository,args.output,args.resume_collar)
