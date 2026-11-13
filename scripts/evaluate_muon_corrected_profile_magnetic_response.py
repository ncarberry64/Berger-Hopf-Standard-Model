"""Corrected-profile same-birth magnetic source through full488 action."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_corrected_profile_magnetic_response import corrected_magnetic_source_sample,corrected_magnetic_sampled_form
from bhsm.interface.muon_electromagnetic_soft_magnetic_source import magnetic_ramp_retarded_application
from bhsm.interface.muon_electromagnetic_magnetic_birth_continuation import magnetic_birth_continuation_application
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output,*,time_nodes=5,time_steps=64):
    out=Path(output);out=out if out.is_absolute() else ROOT/out
    if out.exists():raise FileExistsError('preserve all previous response applications')
    if type(time_nodes)is not int or time_nodes<5 or type(time_steps)is not int or time_steps<16:
        raise ValueError('resolved same-phase coefficient/action and retarded meshes required')
    phases=[load_profile_preserving_phase(p,repository=ROOT) for p in
        ('artifacts/muon_finite_normal_phase_20261011/incoming_run_1','artifacts/muon_inherited_finite_normal_phase_20261011/run_1')]
    if any(p['receipt']['steps']!=1 or p['receipt']['action_parameters']!={'nu_squared_action':4.,'surface_gamma':None} for p in phases):
        raise ValueError('this application binds the declared one-cell nu²4/gamma-unassigned phase pair')
    lengths=[abs(p['receipt']['span']) for p in phases]
    if lengths[0]!=lengths[1]:raise ValueError('same explicit numerical birth arms required')
    L=lengths[0];angular=retained_full_q_angular_space(ROOT);refs={};files={};records=[];forms=[];apps=[]
    config='artifacts/muon_calibrated_pauli_20261009/inputs.json'
    c=json.loads((ROOT/config).read_bytes());e=float(np.sqrt(4*np.pi*c['alpha_consumer']['value']))
    refs[config]=sha256((ROOT/config).read_bytes()).hexdigest()
    times=np.linspace(0,L,time_nodes)
    for phase in phases:
        side=phase['receipt']['side'];origin=-L if side=='incoming' else 0.
        refs.update(phase['input_hashes']);side_apps=[]
        for u in times:
            a=corrected_magnetic_source_sample(phase,float(u+origin),angular,electric_charge=e)
            side_apps.append(a)
            print(json.dumps(dict(stage='corrected_profile_magnetic_full488_action',side=side,time=float(u)),sort_keys=True),flush=True)
        apps.append(side_apps)
        forms.append(corrected_magnetic_sampled_form(times,[a['action']for a in side_apps],duration=L/4))
    q0=apps[0][-1]['source']['connection_source'];q1=apps[1][0]['source']['connection_source']
    birth_defect=float(np.linalg.norm(q0-q1));birth_scale=max(np.linalg.norm(q0),np.linalg.norm(q1))
    if birth_defect>2e-13*birth_scale:raise ValueError('same physical magnetic birth trace is not represented by this common-frame graph')
    birth_rate_jump=float(np.linalg.norm(apps[0][-1]['source']['connection_source_rate']-apps[1][0]['source']['connection_source_rate']))
    incoming=magnetic_ramp_retarded_application(forms[0],time_steps=time_steps)
    print(json.dumps(dict(stage='incoming_retarded_completed',Gauss_relative=incoming['Gauss_relative_maximum']),sort_keys=True),flush=True)
    outgoing=magnetic_birth_continuation_application(forms[1],incoming['state'][-1],time_steps=time_steps)
    out.mkdir(parents=True)
    for phase,side_apps,form,response in zip(phases,apps,forms,(incoming,outgoing)):
        side=phase['receipt']['side'];origin=-L if side=='incoming' else 0.;rep=phase['representation']
        sources=[a['source']for a in side_apps];actions=[a['action']for a in side_apps]
        groups=dict(primal_and_source=dict(times=times,coordinate_times=times+origin,
            raw_fields=np.array([a['raw_sample']['raw_fields']for a in side_apps]),
            Q=np.array([s['connection_source']for s in sources]),Qdot=np.array([s['connection_source_rate']for s in sources]),
            b_source_coefficients=np.array([s['source']for s in sources]),
            s_H=np.array([s['charge_alignment']['unit_Tr16_coefficients']for s in sources]),
            s_H_dot=np.array([s['charge_alignment']['unit_Tr16_coefficient_rate']for s in sources]),
            electromagnetic_wavefunctions=sources[0]['wavefunctions'],wall_trace_map=rep['wall_trace_map'],
            gauge_basis=rep['gauge_basis'],gauge_radial_basis=rep['gauge_radial_basis'],
            source_phase_jacobian=phase['arrays']['stage_jacobian'][0],
            inherited_profile_value_time_radial=np.array([a['inherited_profile_value_time_radial']for a in actions]),
            wall_background_values=np.array([a['wall_background_values']for a in actions])),
            source_first_jets=dict(times=times,Q_first_jet=np.array([s['Q_first_jet']for s in sources]),Qdot_first_jet=np.array([s['Qdot_first_jet']for s in sources])),
            background=dict(times=times,full_background_values=np.array([a['full_background_values']for a in actions])),
            phase=dict(times=response['times'],state=response['state']),
            velocity=dict(times=response['times'],velocity=response['velocity']),
            adjoint=dict(times=response['times'],advanced_adjoint=response['advanced_adjoint'],adjoint_readout_map=response['adjoint_readout_map']),
            contacts={k:v for k,v in response.items()if isinstance(v,np.ndarray)and k not in ('state','velocity','advanced_adjoint','adjoint_readout_map')},
            local_point_jets={k:np.array([s['local_point_jet'][k]for s in sources])for k in sources[0]['local_point_jet']if isinstance(sources[0]['local_point_jet'][k],np.ndarray)})
        for i,key in enumerate(('M','B','K')):
            groups['operator_'+key]=dict(times=times,**{'raw_'+key:np.array([a['raw_forms'][i]for a in actions]),'scalar_'+key:np.array([a['scalar_forms'][i]for a in actions])})
        groups['gauge_rows']=dict(times=times,gauge_weak_rows=np.array([a['gauge_weak_rows']for a in actions]))
        for label,arrays in groups.items():
            path=out/(side+'_'+label+'.npz');deterministic_archive(path,arrays)
            if path.stat().st_size>10*1024**2:raise ValueError('complete lossless output exceeds publication threshold: '+path.name)
            files[path.name]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest(),arrays=sorted(arrays))
        records.append(dict(side=side,coordinate_time_origin=origin,length=L,
            Gauss_relative_maximum=response['Gauss_relative_maximum'],action_boundary_relative_defect=response['action_boundary_relative_defect'],
            adjoint_pairing_maximum_defect=response['adjoint_pairing_maximum_defect'],
            intrinsic_H_response_norm=float(np.linalg.norm(response['intrinsic_H_response'])),
            intrinsic_H_canonical_momentum_norm=float(np.linalg.norm(response['intrinsic_H_canonical_momenta'])),
            gauge_Euler_reaction_norm=float(np.linalg.norm(response['paired_gauge_Euler_reaction'])),
            inherited_profile_minimum_norm=min(float(np.linalg.norm(a['inherited_profile_value_time_radial']))for a in actions),
            inherited_profile_maximum_norm=max(float(np.linalg.norm(a['inherited_profile_value_time_radial']))for a in actions),
            minimum_interior_mass_eigenvalue=form['minimum_interior_mass_eigenvalue'],
            magnetic_curvature_defect=max(s['local_point_jet']['magnetic_curvature_defect']for s in sources),
            numerical_integrator=response['numerical_integrator']))
    names=('muon_corrected_profile_magnetic_response','muon_profile_preserving_phase_sample','muon_parent_positive_coupled_field',
        'muon_exact_material_response','muon_birth_finite_normal_trace_graph','muon_birth_inherited_finite_normal_phase',
        'muon_parent_maxwell_corrected_retarded','muon_reached_trace_action','muon_parent_maxwell_full_retarded',
        'muon_electromagnetic_soft_magnetic_source','muon_electromagnetic_magnetic_birth_continuation','muon_intrinsic_m4_normal_pullback')
    for name in names:
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    for p in (Path(__file__).relative_to(ROOT).as_posix(),'scripts/evaluate_muon_reached_trace_action.py'):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source owner changed')
    result=dict(classification='EVALUATED_CORRECTED_PROFILE_SAME_BIRTH_LOCAL_MAGNETIC_FULL488_RETARDED_RESPONSE',
        input_hashes=refs,array_archives=files,records=records,electric_charge=e,active_source_indices=[0,1,2],inactive_source_indices=[3,4,5,6,7],
        inactive_source_reason='three physical local magnetic first-jet directions only; padded five columns exactly source-defined zero',
        source_scope='background-H-bound linear local magnetic first jet, canonical e once; complete n1 extension includes longitudinal complement',
        source_temporal_profile='incoming C2 smooth turn-on then plateau; outgoing inherits the actual incoming canonical birth x/p and constant plateau',
        birth_source_trace_difference=birth_defect,birth_source_trace_relative_difference=birth_defect/birth_scale,
        birth_material_source_rate_jump=birth_rate_jump,prescribed_birth_profile_value=1.,prescribed_birth_profile_rate=0.,
        birth_graph_scope='common numerical angular/body-frame restriction of reached field trace and canonical-dual graph; global material/bundle reset equality not asserted',
        action_parameters=dict(nu_squared_action=4.,surface_gamma=None),time_nodes=time_nodes,time_steps=time_steps,turn_on_duration=L/4,
        source_motion_before_Gauss=True,source_rate_is_derivative_of_source_Hermite_interpolation=True,
        full_inherited_connection_value_time_radial_retained=True,extra_material_Ar_advection_count=0,
        scalar_Maxwell_relative_normalization=8.,all80_algebraic_Gauss_rows_retained=True,
        same_chronological_background_as_positive_coupled_application=True,
        old_attached_response_or_old_mean_substituted=False,
        global_static_adiabatic_or_quantum_covariance_or_physical_P_strat_completed=False,
        external_LSZ_or_normalized_soft_Pauli_completed=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='Binary64 coefficient/action interpolation and DOP853 finite retarded/advanced source application; mesh/adjoint/Gauss diagnostics are not continuum/operator-rounding/soft-Pauli enclosures. Arm material Qdot jump is retained from actual geometry; common prescribed magnetic trace has g=1,gdot=0 at birth.')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return dict(classification=result['classification'],records=records,birth_source_trace_difference=birth_defect,array_archives=files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--time-nodes',type=int,default=5);p.add_argument('--time-steps',type=int,default=64)
    a=p.parse_args();print(json.dumps(materialize(a.output,time_nodes=a.time_nodes,time_steps=a.time_steps),sort_keys=True))
