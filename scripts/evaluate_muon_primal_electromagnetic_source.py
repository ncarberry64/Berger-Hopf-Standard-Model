"""Solve new H-aligned EM directions on the actual full220 chronological cell."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_primal_electromagnetic_source import (
    retained_phase_source_inputs,electromagnetic_source_sample,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space,SOURCE
from bhsm.interface.muon_trace_enriched_reached_action import enriched_coupled_reached_sample
from bhsm.interface.muon_reached_trace_action import sampled_reached_form,reached_retarded_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(phase_directory,output,*,time_nodes=5,time_steps=64):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    if time_nodes<5 or time_steps<16:raise ValueError('resolved finite source application required')
    bound=retained_phase_source_inputs(phase_directory,repository=ROOT)
    receipt=bound['receipt'];cell=bound['cell'];rep=bound['representation']
    P=bound['cell']['raw_from_phase'] if 'raw_from_phase' in bound['cell'] else None
    from bhsm.interface.muon_birth_trace_enriched_action import generic_coordinate_lift
    P=generic_coordinate_lift(rep['gauge_labels'])['lift'];n=106
    start=cell['initial_x'];end=cell['unknowns'][:n];mid=cell['midpoint_master']
    T=cell['step'];times=np.linspace(0,T,time_nodes)
    angular=retained_full_q_angular_space(ROOT)
    hashes=dict(bound['input_hashes'])
    for name in (SOURCE,'src/bhsm/interface/muon_primal_electromagnetic_source.py',
        'src/bhsm/interface/muon_chronological_charged_current.py',
        'src/bhsm/interface/muon_trace_enriched_reached_action.py',
        'src/bhsm/interface/muon_reached_trace_action.py',
        'src/bhsm/interface/muon_current_source_motion_cubic.py',
        'src/bhsm/interface/muon_primal_trace_enriched_lepton_operator.py',
        'scripts/evaluate_muon_reached_trace_action.py',Path(__file__).relative_to(ROOT).as_posix()):
        hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    rows=[];fields=[];sources=[];samples=[];clifford=[]
    for t in times:
        eta=mid.copy();eta[:n]=(1-t/T)*start+(t/T)*end;raw=P@eta
        source=electromagnetic_source_sample(raw,rep,angular)
        sample=enriched_coupled_reached_sample(raw,rep,angular,source['connection_source'],source['connection_source_rate'],
            nu_squared_action=receipt['action_parameters']['nu_squared_action'])
        fields.append(raw);sources.append(source);samples.append(sample);clifford.append(source['Clifford_application'])
        rows.append(dict(response_time=float(t),coordinate_time=float(t-T if receipt['side']=='incoming' else t),
            H_real=raw[-8:-4].tolist(),H_rate_real=raw[-4:].tolist(),
            unit_Tr16_charge_coefficients=source['charge_alignment']['unit_Tr16_coefficients'].tolist(),
            unit_Tr16_charge_coefficient_rate=source['charge_alignment']['unit_Tr16_coefficient_rate'].tolist(),
            T_b=source['T_b'],T_b_dot=source['T_b_dot'],
            old_source_span_relative_residual=source['old_source_span_relative_residual'],
            local_charge_evolution_commutator_norm=source['local_charge_evolution_commutator_norm'],
            local_charge_covariant_time_norm=source['local_charge_covariant_time_norm'],
            mass_charge_commutator_defect=source['charge_alignment']['mass_charge_commutator_defect'],
            primitive_Clifford_tensor_projection_norm=source['Clifford_application']['Clifford_tensor_projection_norm']))
        print(json.dumps(dict(stage='H_aligned_EM_source_and_full488_action',side=receipt['side'],time=float(t))),flush=True)
    form=sampled_reached_form(times,samples,duration=T/4)
    response=reached_retarded_application(form,time_steps=time_steps)
    out.mkdir(parents=True);archives={}
    groups=dict(
        primal_and_source=dict(times=times,coordinate_times=np.array([r['coordinate_time'] for r in rows]),raw_fields=np.array(fields),
            Q=np.array([s['connection_source'] for s in sources]),Qdot=np.array([s['connection_source_rate'] for s in sources]),
            b_source_coefficients=np.array([s['source'] for s in sources]),
            H_aligned_source_rate=np.array([s['source_rate'] for s in sources]),
            electromagnetic_wavefunctions=sources[0]['wavefunctions'],
            s_H=np.array([s['charge_alignment']['unit_Tr16_coefficients'] for s in sources]),
            s_H_dot=np.array([s['charge_alignment']['unit_Tr16_coefficient_rate'] for s in sources]),
            T_b=np.array([s['T_b'] for s in sources]),T_b_dot=np.array([s['T_b_dot'] for s in sources]),
            wall_trace_map=rep['wall_trace_map'],gauge_basis=rep['gauge_basis'],gauge_radial_basis=rep['gauge_radial_basis'],
            source_phase_jacobian=cell['jacobian']),
        source_first_jets=dict(times=times,Q_first_jet=np.array([s['Q_first_jet'] for s in sources]),
            Qdot_first_jet=np.array([s['Qdot_first_jet'] for s in sources]),
            charged_to_neutral_first_jet=np.array([s['charged_to_neutral_first_jet'] for s in clifford]),
            primitive_Clifford_coefficients=np.array([s['Clifford_coefficients'] for s in clifford])),
        operators=dict(raw_M=np.array([s['raw_forms'][0] for s in samples]),raw_B=np.array([s['raw_forms'][1] for s in samples]),
            raw_K=np.array([s['raw_forms'][2] for s in samples]),scalar_M=np.array([s['scalar_forms'][0] for s in samples]),
            scalar_B=np.array([s['scalar_forms'][1] for s in samples]),scalar_K=np.array([s['scalar_forms'][2] for s in samples]),
            gauge_weak_rows=np.array([s['gauge_weak_rows'] for s in samples])),
        phase=dict(times=response['times'],state=response['state']),velocity=dict(times=response['times'],velocity=response['velocity']),
        adjoint=dict(times=response['times'],advanced_adjoint=response['advanced_adjoint'],adjoint_readout_map=response['adjoint_readout_map']),
        contacts={k:v for k,v in response.items() if isinstance(v,np.ndarray) and k not in ('state','velocity','advanced_adjoint','adjoint_readout_map')})
    for name,arrays in groups.items():
        target=out/(name+'.npz');deterministic_archive(target,arrays)
        if target.stat().st_size>10*1024**2:raise ValueError('lossless archive needs a further split')
        archives[target.name]=dict(bytes=target.stat().st_size,sha256=sha256(target.read_bytes()).hexdigest(),arrays=sorted(arrays))
    if hashes!={path:sha256((ROOT/path).read_bytes()).hexdigest() for path in hashes}:raise RuntimeError('consumed owner changed')
    result=dict(classification='EVALUATED_HIGGS_ALIGNED_ELECTROMAGNETIC_FULL488_SAME_ACTION_RESPONSE',
        input_hashes=hashes,side=receipt['side'],array_archives=archives,actual_phase_span=receipt['span'],
        chronological_response_span=T,source_phase_jacobian_chronological=True,
        action_parameters=receipt['action_parameters'],time_nodes=time_nodes,time_steps=time_steps,source_pulse_duration=T/4,
        source_basis='actual local H-selected Q_H=T_H+Y times retained eight coexact photon wavefunctions; all full400 components before Gauss',
        source_frame_rate='future coordinate Hdot and geometric Tb_dot; Qdot=Tb_dot S(H)+Tb D_H S(H)Hdot exactly once',
        b_source_coefficients_time_dependent=True,source_motion_count=1,source_motion_before_Gauss=True,
        source_first_jets_are_analytic=True,sources=rows,
        Gauss_relative_maximum=response['Gauss_relative_maximum'],
        action_boundary_relative_defect=response['action_boundary_relative_defect'],
        adjoint_pairing_maximum_defect=response['adjoint_pairing_maximum_defect'],
        intrinsic_H_response_norm=float(np.linalg.norm(response['intrinsic_H_response'])),
        intrinsic_H_canonical_norm=float(np.linalg.norm(response['intrinsic_H_canonical_momenta'])),
        scalar_wall_current_norm=float(np.linalg.norm(response['intrinsic_scalar_wall_current_pairing'])),
        gauge_Euler_reaction_norm=float(np.linalg.norm(response['paired_gauge_Euler_reaction'])),
        minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],numerical_integrator=response['numerical_integrator'],
        source_coordinate='unit charged connection beta=Tb*b; canonical Omega=-i e Q_H A_can needs consistent action/current residue matching',
        field_bridge='actual same chronological cell x linear, future v/y held at solved midpoint; finite temporal interpolation only',
        external_soft_momentum_selected=False,external_LSZ_or_open_fermion_vertex_completed=False,
        primitive_Clifford_tensor_zero_is_native_Pauli_zero=False,
        old_transported_Q8_inverse_substituted=False,complete_a_mu=None,complete_g_mu=None,complete_observable=False,
        physical_Pauli_value=False,action_selected=False,Gate7_closed=False,
        error_scope='actual finite retarded/advanced action application with Gauss and temporal contacts; ODE/mesh diagnostics, not continuum/operator-rounding/soft-Pauli enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(side=result['side'],array_archives=archives,Gauss_relative_maximum=result['Gauss_relative_maximum'],
        action_boundary_relative_defect=result['action_boundary_relative_defect'],adjoint_pairing_maximum_defect=result['adjoint_pairing_maximum_defect'],
        intrinsic_H_response_norm=result['intrinsic_H_response_norm'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--time-nodes',type=int,default=5);p.add_argument('--time-steps',type=int,default=64)
    a=p.parse_args();print(json.dumps(materialize(a.phase_directory,a.output,time_nodes=a.time_nodes,time_steps=a.time_steps),sort_keys=True))
