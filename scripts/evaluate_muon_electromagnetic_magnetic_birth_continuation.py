"""Apply an actual local magnetic first jet after compatible retarded turn-on."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_primal_electromagnetic_source import (
    retained_phase_source_inputs,
)
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space,SOURCE
from bhsm.interface.muon_trace_enriched_reached_action import enriched_coupled_reached_sample
from bhsm.interface.muon_reached_trace_action import sampled_reached_form
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import magnetic_source_sample
from bhsm.interface.muon_electromagnetic_magnetic_birth_continuation import magnetic_birth_continuation_application
from bhsm.interface.muon_parent_maxwell_full_retarded import _reduced_at
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(phase_directory,output,*,incoming_application,time_nodes=5,time_steps=64):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve previous applications')
    if time_nodes<5 or time_steps<16:raise ValueError('resolved finite source application required')
    bound=retained_phase_source_inputs(phase_directory,repository=ROOT)
    receipt=bound['receipt'];cell=bound['cell'];rep=bound['representation']
    if receipt['side']!='outgoing':raise ValueError('outgoing common magnetic continuation required')
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
    config_path=ROOT/'artifacts/muon_calibrated_pauli_20261009/inputs.json'
    config=json.loads(config_path.read_bytes());electric_charge=float(np.sqrt(4*np.pi*config['alpha_consumer']['value']))
    hashes[config_path.relative_to(ROOT).as_posix()]=sha256(config_path.read_bytes()).hexdigest()
    name='src/bhsm/interface/muon_electromagnetic_soft_magnetic_source.py';hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    rows=[];fields=[];sources=[];samples=[];clifford=[]
    for t in times:
        eta=mid.copy();eta[:n]=(1-t/T)*start+(t/T)*end;raw=P@eta
        source=magnetic_source_sample(raw,rep,angular,electric_charge=electric_charge)
        sample=enriched_coupled_reached_sample(raw,rep,angular,source['connection_source'],source['connection_source_rate'],
            nu_squared_action=receipt['action_parameters']['nu_squared_action'])
        fields.append(raw);sources.append(source);samples.append(sample);clifford.append(source['Clifford_application'])
        rows.append(dict(response_time=float(t),coordinate_time=float(t-T if receipt['side']=='incoming' else t),
            H_real=raw[-8:-4].tolist(),H_rate_real=raw[-4:].tolist(),
            unit_Tr16_charge_coefficients=source['charge_alignment']['unit_Tr16_coefficients'].tolist(),
            unit_Tr16_charge_coefficient_rate=source['charge_alignment']['unit_Tr16_coefficient_rate'].tolist(),
            canonical_magnetic_factor=source['canonical_magnetic_factor'],canonical_magnetic_factor_rate=source['canonical_magnetic_factor_rate'],
            old_source_span_relative_residual=source['old_coexact_relative_remainder'],
            local_charge_evolution_commutator_norm=source['local_charge_evolution_commutator_norm'],
            local_charge_covariant_time_norm=source['local_charge_covariant_time_norm'],
            mass_charge_commutator_defect=source['charge_alignment']['mass_charge_commutator_defect'],
            primitive_Clifford_tensor_projection_norm=source['Clifford_application']['Clifford_tensor_projection_norm']))
        print(json.dumps(dict(stage='local_magnetic_jet_and_full488_action',side=receipt['side'],time=float(t))),flush=True)
    form=sampled_reached_form(times,samples,duration=T/4)
    ip=Path(incoming_application);ip=ip if ip.is_absolute() else ROOT/ip
    incoming=json.loads((ip/'result.json').read_bytes())
    if incoming['classification']!='EVALUATED_HIGGS_ALIGNED_LOCAL_MAGNETIC_JET_FULL488_RESPONSE' or incoming['side']!='incoming' or incoming['source_final_value']!=1 or incoming['source_final_rate']!=0:
        raise ValueError('actual incoming magnetic plateau birth response required')
    for path,digest in incoming['input_hashes'].items():
        if sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('incoming owner changed: '+path)
        hashes[path]=digest
    for name,record in incoming['array_archives'].items():
        if sha256((ip/name).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('incoming magnetic response archive changed: '+name)
        hashes[(ip/name).relative_to(ROOT).as_posix()]=record['sha256']
    hashes[(ip/'result.json').relative_to(ROOT).as_posix()]=sha256((ip/'result.json').read_bytes()).hexdigest()
    name='src/bhsm/interface/muon_electromagnetic_magnetic_birth_continuation.py';hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    name='src/bhsm/interface/muon_birth_paired_field_endpoint.py';hashes[name]=sha256((ROOT/name).read_bytes()).hexdigest()
    with np.load(ip/'phase.npz',allow_pickle=False) as a:incoming_state=a['state'][-1].copy()
    with np.load(ip/'primal_and_source.npz',allow_pickle=False) as a:incoming_birth_Q=a['Q'][-1].copy()
    with np.load(ip/'velocity.npz',allow_pickle=False) as a:incoming_birth_velocity=a['velocity'][-1].copy()
    response=magnetic_birth_continuation_application(form,incoming_state,time_steps=time_steps)
    f0=_reduced_at(form,0.);initial=response['state'][0];initial_velocity=response['velocity'][0]
    outgoing_p=f0['M'][:400,:400]@initial_velocity+f0['B'][:400,:400].T@initial[:400]+f0['B'][400:,:400].T
    matching=dict(field_trace_coefficient_jump_norm=float(np.linalg.norm(initial[:400]-incoming_state[:400])),
        canonical_dual_jump_norm=float(np.linalg.norm(outgoing_p-incoming_state[400:])),
        prescribed_birth_source_trace_jump_norm=float(np.linalg.norm(sources[0]['connection_source']-incoming_birth_Q)),
        future_velocity_jump_norm=float(np.linalg.norm(initial_velocity-incoming_birth_velocity)),
        outgoing_initial_Gauss_relative=float(np.max(abs(response['Gauss_residual'][0]))/(1+np.max(abs(response['A_tau'][0])))),
        field_graph_owner='muon_birth_paired_field_endpoint.paired_field_endpoint_rows dynamic/H trace and canonical-dual equations',
        actual_source_initial_state_supplied_from_incoming_birth=True,
        copied_incoming_velocity=False,extra_metric_density_multiplied=False,
        pointwise_common_frame_graph_restriction=True,global_worldvolume_bundle_reset_evaluated=False)
    out.mkdir(parents=True);archives={}
    groups=dict(
        local_point_jets={key:np.array([s['local_point_jet'][key] for s in sources]) for key in sources[0]['local_point_jet'] if isinstance(sources[0]['local_point_jet'][key],np.ndarray)},
        primal_and_source=dict(times=times,coordinate_times=np.array([r['coordinate_time'] for r in rows]),raw_fields=np.array(fields),
            Q=np.array([s['connection_source'] for s in sources]),Qdot=np.array([s['connection_source_rate'] for s in sources]),
            b_source_coefficients=np.array([s['source'] for s in sources]),
            H_aligned_source_rate=np.array([s['source_rate'] for s in sources]),
            electromagnetic_wavefunctions=sources[0]['wavefunctions'],
            s_H=np.array([s['charge_alignment']['unit_Tr16_coefficients'] for s in sources]),
            s_H_dot=np.array([s['charge_alignment']['unit_Tr16_coefficient_rate'] for s in sources]),
            canonical_magnetic_factor=np.array([s['canonical_magnetic_factor'] for s in sources]),canonical_magnetic_factor_rate=np.array([s['canonical_magnetic_factor_rate'] for s in sources]),
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
    result=dict(classification='EVALUATED_COMMON_BIRTH_LOCAL_MAGNETIC_JET_FULL488_CONTINUATION',birth_source_matching=matching,
        source_scope='physical_local_magnetic_first_jet',active_source_indices=[0,1,2],inactive_source_indices=[3,4,5,6,7],
        inactive_source_reason='only three magnetic axes inserted; five padded source columns identically zero by definition',
        electric_charge=electric_charge,canonical_current='chi_hat=R4^(3/2)psi/(2pi²)',
        source_temporal_profile='constant_magnetic_trace_inherited_from_incoming_birth',turn_on_duration=None,
        source_midpoint_value=1.,source_midpoint_rate=0.,source_final_value=1.,source_final_rate=0.,
        global_static_or_adiabatic_matching_proved=False,outgoing_common_birth_graph_restriction_applied=True,
        input_hashes=hashes,side=receipt['side'],array_archives=archives,actual_phase_span=receipt['span'],
        chronological_response_span=T,source_phase_jacobian_chronological=True,
        action_parameters=receipt['action_parameters'],time_nodes=time_nodes,time_steps=time_steps,source_pulse_duration=None,integration_step_reference_duration=T/4,
        source_basis='actual local H-selected Q_H=T_H+Y times three canonical uniform-B first jets in complete n1/right-coframe space including longitudinal complement; full400 before Gauss',
        source_frame_rate='future coordinate Hdot and R4dot; Qdot=e R4 R4dot S(H)+(e R4²/2) D_H S(H)Hdot once',
        b_source_coefficients_time_dependent=True,source_motion_count=1,source_motion_before_Gauss=True,
        source_first_jets_are_analytic=True,sources=rows,
        point_potential_zero_defect_maximum=max(s['local_point_jet']['potential_zero_defect'] for s in sources),
        point_magnetic_curvature_defect_maximum=max(s['local_point_jet']['magnetic_curvature_defect'] for s in sources),
        nonlinear_angular_H_axis_response_included=False,
        Gauss_relative_maximum=response['Gauss_relative_maximum'],
        action_boundary_relative_defect=response['action_boundary_relative_defect'],
        adjoint_pairing_maximum_defect=response['adjoint_pairing_maximum_defect'],
        intrinsic_H_response_norm=float(np.linalg.norm(response['intrinsic_H_response'])),
        intrinsic_H_canonical_norm=float(np.linalg.norm(response['intrinsic_H_canonical_momenta'])),
        scalar_wall_current_norm=float(np.linalg.norm(response['intrinsic_scalar_wall_current_pairing'])),
        gauge_Euler_reaction_norm=float(np.linalg.norm(response['paired_gauge_Euler_reaction'])),
        minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],numerical_integrator=response['numerical_integrator'],
        source_coordinate='Omega=-i e Q_H A_can; A_can=B cross X/2; e once; B is local action-unit magnetic curvature, not a Fourier q',
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
    p.add_argument('--incoming-application',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize(a.phase_directory,a.output,incoming_application=a.incoming_application,time_nodes=a.time_nodes,time_steps=a.time_steps),sort_keys=True))
