"""Solve fresh Maxwell/Higgs responses on the actual corrected one-cell phase."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_birth_trace_enriched_phase import load_enriched_endpoint
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_current_source_motion_cubic import current_face_source_jets
from bhsm.interface.muon_trace_enriched_reached_action import enriched_coupled_reached_sample
from bhsm.interface.muon_reached_trace_action import sampled_reached_form,reached_retarded_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(phase_directory,output,*,time_nodes=5,time_steps=64):
    phase=Path(phase_directory);phase=phase if phase.is_absolute() else ROOT/phase
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve earlier applications; choose a new output directory')
    receipt=json.loads((phase/'result.json').read_text(encoding='utf8'))
    if receipt['steps']!=1 or receipt['completed_steps']!=1 or receipt['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
        raise ValueError('actual converged one-cell phase required')
    if sha256((phase/'application.npz').read_bytes()).hexdigest()!=receipt['numerical_sha256']:raise ValueError('phase archive mismatch')
    loaded=load_enriched_endpoint(receipt['consumed_paired_endpoint_path'],side=receipt['side'])
    rep=loaded['representation'];P=loaded['coordinates']['lift'];nx=loaded['coordinates']['x_count']
    with np.load(phase/'application.npz',allow_pickle=False) as f:
        initial_master=f['initial_master'];final_x=f['x_final'];mid_raw=f['stage_midpoint_raw'][0]
        source_phase_jacobian=f['stage_jacobian'][0]
    eta_mid=P.T@mid_raw
    if not np.array_equal(P@eta_mid,mid_raw):raise ValueError('complete actual midpoint lift required')
    span=receipt['span'];T=abs(span)
    if time_nodes<5 or time_steps<16:raise ValueError('resolved source action nodes and integration steps required')
    times=np.linspace(0,T,time_nodes);x0=initial_master[:nx]
    angular=retained_full_q_angular_space(ROOT);b=angular['source_coefficients']
    if b.shape!=(400,8) or np.any(b[:160]):raise ValueError('inherited spatial eight-source action image required')
    refs=[phase/'result.json',phase/'application.npz',ROOT/'src/bhsm/interface/muon_trace_enriched_reached_action.py',
        ROOT/'src/bhsm/interface/muon_reached_trace_action.py',ROOT/'src/bhsm/interface/muon_current_source_motion_cubic.py',
        ROOT/'src/bhsm/interface/muon_birth_trace_enriched_phase.py',ROOT/'scripts/evaluate_muon_reached_trace_action.py',Path(__file__)]
    hashes=dict(receipt['input_hashes'])
    hashes.update({p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    fields=[];Q=[];Qt=[];samples=[];tb=[];tbd=[];coordinate_times=[]
    for t in times:
        fraction=t/T if span>0 else 1-t/T
        eta=eta_mid.copy();eta[:nx]=(1-fraction)*x0+fraction*final_x;raw=P@eta
        source=current_face_source_jets(raw[:100]);value,rate=source['T_b'].value,source['T_b_dot'].value
        current=value*b;current_rate=rate*b
        sample=enriched_coupled_reached_sample(raw,rep,angular,current,current_rate,
            nu_squared_action=receipt['action_parameters']['nu_squared_action'])
        fields.append(raw);Q.append(current);Qt.append(current_rate);samples.append(sample);tb.append(value);tbd.append(rate)
        coordinate_times.append(t if span>0 else t-T)
    form=sampled_reached_form(times,samples,duration=T/4)
    response=reached_retarded_application(form,time_steps=time_steps)
    if hashes!={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in hashes}:raise RuntimeError('consumed action owner changed')
    out.mkdir(parents=True);archives={}
    groups=dict(
        primal_and_source=dict(times=times,coordinate_times=np.array(coordinate_times),raw_fields=np.array(fields),
            Q=np.array(Q),Qdot=np.array(Qt),b_source_coefficients=b,T_b=np.array(tb),T_b_dot=np.array(tbd),
            wall_trace_map=rep['wall_trace_map'],gauge_basis=rep['gauge_basis'],gauge_radial_basis=rep['gauge_radial_basis'],
            source_phase_jacobian=source_phase_jacobian),
        operators=dict(raw_M=np.array([s['raw_forms'][0] for s in samples]),raw_B=np.array([s['raw_forms'][1] for s in samples]),
            raw_K=np.array([s['raw_forms'][2] for s in samples]),scalar_M=np.array([s['scalar_forms'][0] for s in samples]),
            scalar_B=np.array([s['scalar_forms'][1] for s in samples]),scalar_K=np.array([s['scalar_forms'][2] for s in samples]),
            gauge_weak_rows=np.array([s['gauge_weak_rows'] for s in samples])),
        phase=dict(times=response['times'],state=response['state']),velocity=dict(times=response['times'],velocity=response['velocity']),
        adjoint=dict(times=response['times'],advanced_adjoint=response['advanced_adjoint'],adjoint_readout_map=response['adjoint_readout_map']),
        contacts={k:v for k,v in response.items() if isinstance(v,np.ndarray) and k not in ('state','velocity','advanced_adjoint','adjoint_readout_map')})
    for name,arrays in groups.items():
        target=out/(name+'.npz');deterministic_archive(target,arrays)
        if target.stat().st_size>10*1024**2:raise ValueError('complete arrays require a further lossless split')
        archives[target.name]=dict(bytes=target.stat().st_size,sha256=sha256(target.read_bytes()).hexdigest(),arrays=sorted(arrays))
    result=dict(classification='EVALUATED_FRESH_COUPLED_REACHED_RESPONSE_ON_ACTUAL_ENRICHED_PHASE',
        input_hashes=hashes,side=receipt['side'],array_archives=archives,
        actual_phase_span=span,coordinate_time_interval=[coordinate_times[0],coordinate_times[-1]],
        actual_nonlinear_phase_scaled_residual=receipt['stages'][0]['scaled_residual'],
        field_bridge='same variational one-cell x(t) linear; actual v/y midpoint held; not an independently solved continuous history',
        source_basis='all inherited spatial full400x8 b test columns; Tb/Tbdot from actual phase geometry; no physical current/covariance selected',
        source_motion_count=1,source_motion_before_Gauss=True,old_source_or_H_response_substituted=False,
        exact_affine_radial_background_image_retained=True,response_radial_scope=samples[0]['response_radial_scope'],
        time_nodes=time_nodes,time_steps=time_steps,source_pulse_duration=T/4,
        source_pulse_scope='compact numerical Green application inside the actual finite cell, not physical soft transfer or E0 selection',
        action_parameters=receipt['action_parameters'],
        Gauss_relative_maximum=response['Gauss_relative_maximum'],
        action_boundary_relative_defect=response['action_boundary_relative_defect'],
        adjoint_pairing_maximum_defect=response['adjoint_pairing_maximum_defect'],
        intrinsic_H_response_norm=float(np.linalg.norm(response['intrinsic_H_response'])),
        intrinsic_H_canonical_norm=float(np.linalg.norm(response['intrinsic_H_canonical_momenta'])),
        scalar_wall_current_norm=float(np.linalg.norm(response['intrinsic_scalar_wall_current_pairing'])),
        gauge_Euler_reaction_norm=float(np.linalg.norm(response['paired_gauge_Euler_reaction'])),
        minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],
        numerical_integrator=response['numerical_integrator'],
        error_scope='finite ODE/quadrature/source-adjoint and Gauss checks on the exact saved numerical phase bridge; no continuum or physical Pauli bound',
        physical_birth_formation_closed=False,complete_relative_native_domain=False,physical_Pauli_value=False,
        action_selected=False,Gate7_closed=False,complete_observable=False)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return {k:result[k] for k in ('side','Gauss_relative_maximum','action_boundary_relative_defect','adjoint_pairing_maximum_defect',
        'intrinsic_H_response_norm','intrinsic_H_canonical_norm','scalar_wall_current_norm','gauge_Euler_reaction_norm','array_archives')}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--time-nodes',type=int,default=5);p.add_argument('--time-steps',type=int,default=64)
    a=p.parse_args();print(json.dumps(materialize(a.phase_directory,a.output,time_nodes=a.time_nodes,time_steps=a.time_steps),sort_keys=True))
