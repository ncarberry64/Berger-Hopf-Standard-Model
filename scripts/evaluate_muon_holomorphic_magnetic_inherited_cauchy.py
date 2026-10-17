"""Actual-born reconstitution and inherited source-on child action/current."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import (original_signed_stage,signed_n1_forms,signed_n1_form_first,
    holomorphic_local_B_trace,magnetic_unsquared_unit_em_current,magnetic_angular_trace,original_named_wall_lift,complete_gauge_wall_constraints)
from bhsm.interface.muon_holomorphic_n1_magnetic_cauchy import magnetic_trace_time_germ,magnetic_trace_time_first
from bhsm.interface.muon_holomorphic_magnetic_birth_matching import signed_field_face_reconstruction,inherited_birth_interior_reconstitution,original_birth_field_rows
from bhsm.interface.muon_holomorphic_magnetic_birth_source_contacts import magnetic_birth_source_contacts
from bhsm.interface.muon_holomorphic_magnetic_inherited_cauchy import (inherited_prescribed_magnetic_prefix,
    actual_owner_piecewise_source_germ,signed_field_face_source_first)
from bhsm.interface.muon_holomorphic_child_action import _affine_geometry
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve inherited source-on continuation')
    pins={};archives={}
    def read(p,expected=None):
        p=ROOT/p if not p.is_absolute()else p;b=p.read_bytes();h=sha256(b).hexdigest()
        if not p.is_relative_to(ROOT):raise ValueError('same checkout input required')
        pins[p.relative_to(ROOT).as_posix()]=h
        if expected is not None and h!=expected:raise ValueError('same actual action/source pin differs')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    root=ROOT/'artifacts/muon_changing_canonical_source_20261012/run_3';rm=read(root/'result.json')
    birth=ROOT/'artifacts/muon_holomorphic_magnetic_birth_matching_20261012/run_1';bm=read(birth/'result.json')
    tf=ROOT/'artifacts/muon_coupled_reset_canonical_trace_20261012/run_1';tm=read(tf/'result.json');trace=read(tf/'application.npz',tm['archives']['application.npz']['sha256'])
    phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];P=phase['coordinates']['lift'];pair=trace['raw_pair'];refs=trace['reference_pair']
    config=read(Path('artifacts/muon_calibrated_pauli_20261009/inputs.json'));charge=float(np.sqrt(4*np.pi*config['alpha_consumer']['value']))
    angular=magnetic_angular_trace();parameters=rm['action_parameters'];knots=np.array([0,.25,.5,.75,1.]);prepared=[]
    for case in('normal_basis','area_source'):
        bdata=read(birth/f'{case}_actual_birth_source_and_original_reset_rows.npz',bm['archives'][f'{case}_actual_birth_source_and_original_reset_rows.npz']['sha256'])
        parent_integrated=read(birth/f'{case}_parent_finite_prefix_face.npz',bm['archives'][f'{case}_parent_finite_prefix_face.npz']['sha256'])
        ps=read(root/f'{case}_consumed_birth_parent_source.npz',rm['archives'][f'{case}_consumed_birth_parent_source.npz']['sha256'])
        cs=read(root/f'{case}_consumed_birth_child_source.npz',rm['archives'][f'{case}_consumed_birth_child_source.npz']['sha256'])
        dirs=[np.column_stack([P@s['direction_'+q]for q in('high','low')])for s in(ps,cs)]
        births=[original_signed_stage(pair[a],dirs[a],pair[0],dirs[0],refs,np.zeros((2,268,2),complex),rep,
            side='parent'if a==0 else'child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=parameters['nu_squared_action'])for a in(0,1)]
        bornforms=[signed_n1_forms(b,angular)for b in births];bornfirst=[signed_n1_form_first(b,angular)for b in births]
        bornQ=[holomorphic_local_B_trace(pair[a],dirs[a],births[a]['stage'],electric_charge=charge,angular=angular)for a in(0,1)]
        incoming=ROOT/f'artifacts/muon_holomorphic_n1_magnetic_action_20261012/incoming_{case}_run_1';im=read(incoming/'result.json')
        ip=read(incoming/'actual_zero_Cauchy_magnetic_prefix.npz',im['archives']['actual_zero_Cauchy_magnetic_prefix.npz']['sha256'])
        ss=[read(incoming/f'stage_{j}_actual_magnetic_trace.npz',im['archives'][f'stage_{j}_actual_magnetic_trace.npz']['sha256'])for j in ip['original_stage_order']]
        oldf=read(incoming/'stage_0_original_signed_forms.npz',im['archives']['stage_0_original_signed_forms.npz']['sha256'])
        olddf={n:[]for n in('K','M','B_forward','B_reverse')}
        for label in('high','low'):
            d=read(incoming/f'stage_0_original_signed_forms_first_{label}.npz',im['archives'][f'stage_0_original_signed_forms_first_{label}.npz']['sha256'])
            for n in olddf:olddf[n].append(d[n])
        olddf={n:np.array(v)for n,v in olddf.items()};ids=births[0]['value_permutation'];lifts=births[0]['lifts']
        S=ip['original_interior_field_lift'];L=np.kron(original_named_wall_lift(rep,ids),np.eye(4));na=48;Sd=S[:,na:]
        wallfirst=magnetic_trace_time_first(1.,ss,sum(ip['future_coordinate_steps']))
        integrated_first=signed_field_face_source_first(oldf,olddf,S,L,wallfirst,ip['final_reduced_canonical_state_first'],parent_integrated,na)
        # Actual parent birth action, with preserved free q/Pi and actual
        # Q/Qt, is reconstructed before the child. No held-rate admission.
        parent_born=inherited_birth_interior_reconstitution(bornforms[0],S,L,parent_integrated['total_field'],parent_integrated['canonical_momentum'],
            (bornQ[0]['Q'],bornQ[0]['Q_coordinate_time']),na)
        zfirst=np.array([np.r_[Sd.T@(integrated_first['total_field_first'][k]-L@bornQ[0]['Q_first'][k].reshape(80,3)),
            Sd.T@integrated_first['canonical_momentum_first'][k]]for k in range(2)])
        parent_first=signed_field_face_source_first(bornforms[0],bornfirst[0],S,L,(bornQ[0]['Q_first'],bornQ[0]['Q_coordinate_time_first']),zfirst,parent_born,na)
        child_born=inherited_birth_interior_reconstitution(bornforms[1],S,L,parent_born['total_field'],parent_born['canonical_momentum'],
            (bornQ[1]['Q'],bornQ[1]['Q_coordinate_time']),na)
        childinitial=np.array([np.r_[Sd.T@(parent_first['total_field_first'][k]-L@bornQ[1]['Q_first'][k].reshape(80,3)),
            Sd.T@parent_first['canonical_momentum_first'][k]]for k in range(2)])
        contact=magnetic_birth_source_contacts(parent_born,child_born,complete_gauge_wall_constraints(lifts,4)['constraint'],S,L,
            np.kron(lifts['frame_rows'],np.eye(4)),bornQ[0]['Q'],bornQ[1]['Q'])
        child_first=signed_field_face_source_first(bornforms[1],bornfirst[1],S,L,(bornQ[1]['Q_first'],bornQ[1]['Q_coordinate_time_first']),childinitial,child_born,na)
        contact.update(source_first_inherited_value_jump=child_first['total_field_first']-parent_first['total_field_first'],
            source_first_free_momentum_jump=np.einsum('af,kfs->kas',Sd.T,child_first['canonical_momentum_first']-parent_first['canonical_momentum_first']),
            direct_source_first_endpoint_cotangent=np.array([(L@bornQ[0]['Q_first'][k].reshape(80,3)).T@parent_born['canonical_momentum']
                -(L@bornQ[1]['Q_first'][k].reshape(80,3)).T@child_born['canonical_momentum']for k in range(2)]),
            actual_parent_birth_momentum_minus_finite_prefix=parent_born['canonical_momentum']-parent_integrated['canonical_momentum'],
            actual_parent_birth_field_minus_finite_prefix=parent_born['total_field']-parent_integrated['total_field'])
        source_nodes=[bornQ[1]];bindings=[];forms=[];formsfirst=[];provenance=[];steps=[]
        for j in range(2):
            name=f'outgoing_{j:04d}_{case}_source_response.npz';a=read(root/name,rm['archives'][name]['sha256']);dd=lambda k:np.column_stack((a[k+'_high'],a[k+'_low']))
            b=original_signed_stage(a['stage_raw'],dd('stage_raw_direction'),a['parent_source_stage_raw'],dd('parent_source_stage_raw_direction'),
                a['reference_stage_pair'],np.stack((a['reference_stage_direction_high'],a['reference_stage_direction_low']),axis=-1),rep,
                side='child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=parameters['nu_squared_action'])
            bindings.append(b);forms.append(signed_n1_forms(b,angular));formsfirst.append(signed_n1_form_first(b,angular));steps.append(a['coordinate_time_step'].item())
            source_nodes.append(holomorphic_local_B_trace(a['stage_raw'],dd('stage_raw_direction'),b['stage'],electric_charge=charge,angular=angular))
            provenance.append(name)
            ename=f'outgoing_{j:04d}_{case}_endpoint_source_response.npz';e=read(root/ename,rm['archives'][ename]['sha256']);t=e['endpoint_time'].item()
            parent=_affine_geometry(pair[0],t);dp=np.column_stack([_affine_geometry(dirs[0][:,k],t)for k in range(2)])
            rr=np.array([_affine_geometry(r,t)for r in refs]);ed=np.column_stack((e['endpoint_raw_direction_high'],e['endpoint_raw_direction_low']))
            eb=original_signed_stage(e['endpoint_raw'],ed,parent,dp,rr,np.zeros((2,268,2),complex),rep,
                side='child',lambda_H=rep['scalar_matching']['lambda_H'],nu_squared_action=parameters['nu_squared_action'])
            source_nodes.append(holomorphic_local_B_trace(e['endpoint_raw'],ed,eb['stage'],electric_charge=charge,angular=angular));provenance.append(ename)
        prepared.append((case,parent_integrated,parent_born,child_born,contact,parent_first,child_first,
            np.r_[child_born['canonical_state'][None],childinitial],source_nodes,bindings,forms,formsfirst,np.array(steps),provenance))
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_holomorphic_magnetic_inherited_cauchy.py',
            'tests/test_muon_holomorphic_magnetic_birth_source_contacts.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    def save(name,a):
        p=out/name;_compressed_npz(p,{k:v for k,v in a.items()if isinstance(v,np.ndarray)})
        if p.stat().st_size>=10*1024**2:raise ValueError('split source/current outputs below10MiB')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    maximum=lambda a:float(np.max(abs(a)));reports={}
    for case,integrated,parent,child,contact,parentfirst,childfirst,initial,sources,bindings,forms,formsfirst,steps,provenance in prepared:
        free_max=max(maximum(contact[k])for k in('momentum_full_free_projection','Gauss_full_free_projection','momentum_named_constraint_range_defect','Gauss_named_constraint_range_defect'))
        if free_max>2e-10:raise ValueError('actual source-domain/free rows fail; do not launch inherited continuation')
        save(case+'_actual_birth_reconstitution_and_source_contacts.npz',dict(contact,**{'parent_'+k:v for k,v in parent.items()if isinstance(v,np.ndarray)},
            **{'child_'+k:v for k,v in child.items()if isinstance(v,np.ndarray)},**{'parent_'+k:v for k,v in parentfirst.items()if isinstance(v,np.ndarray)},
            **{'child_'+k:v for k,v in childfirst.items()if isinstance(v,np.ndarray)},initial_canonical_state=initial,
            source_knots=knots,actual_Q=np.array([s['Q']for s in sources]),actual_Qt=np.array([s['Q_coordinate_time']for s in sources]),
            actual_Q_first=np.array([s['Q_first']for s in sources]),actual_Qt_first=np.array([s['Q_coordinate_time_first']for s in sources])))
        germ=lambda t:actual_owner_piecewise_source_germ(t,knots,sources,sum(steps))
        firstgerm=lambda t:actual_owner_piecewise_source_germ(t,knots,sources,sum(steps),first=True)
        response=inherited_prescribed_magnetic_prefix(forms,steps,sources,rep,bindings[0]['value_permutation'],initial,germ,
            source_first_time_germ=firstgerm,source_knots=knots[1:-1],forms_first=formsfirst)
        save(case+'_inherited_on_source_canonical_response.npz',response)
        points={n:np.array([r[n]for r in response['point_sources']])for n in response['point_sources'][0]}
        save(case+'_inherited_on_source_points.npz',points)
        current=magnetic_unsquared_unit_em_current(bindings,steps,response);save(case+'_inherited_on_source_unsquared_current.npz',current)
        report=dict(case=case,free_domain_and_constraint_dual_range_max=free_max,
            actual_source_endpoint_cotangent_norm=float(np.linalg.norm(contact['prescribed_source_action_cotangent'])),
            actual_source_cotangent_diagonal=[[float(v.real),float(v.imag)]for v in np.diag(contact['prescribed_source_action_cotangent'])],
            source_At_Gauss_pairing_max=maximum(contact['source_At_Gauss_pairing']),named_frame_source_max=maximum(contact['named_frame_source_rows']),
            full_minus_source_action_cotangent_max=maximum(contact['full_minus_source_action_cotangent']),
            fresh_parent_full_momentum_change=maximum(contact['actual_parent_birth_momentum_minus_finite_prefix']),
            initial_source_first_value_jump_max=maximum(contact['source_first_inherited_value_jump']),
            initial_source_first_free_momentum_jump_max=maximum(contact['source_first_free_momentum_jump']),
            original_propagated_rows_max=response['original_reconstructed_rows_max'],source_points=len(points['cell']),
            final_state_norm=float(np.linalg.norm(response['final_reduced_canonical_state'])),
            final_source_first_norms=[float(np.linalg.norm(v))for v in response['final_reduced_canonical_state_first']],
            current_terms={n:float(np.linalg.norm(current[n]))for n in('operator_insertion','right_current_motion','literal_left_motion','total')},
            current_first_norms=[float(np.linalg.norm(v))for v in current['total_first']],actual_source_germ_provenance=provenance,
            source_on_at_birth=True,child_C2_pulse_not_restarted=True,conditional_prescribed_source_domain_continuation=True,
            physical_full_coupled_birth_mode_exterior_or_pole_matched=False)
        reports[case]=report;print(json.dumps(report,sort_keys=True),flush=True)
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('same action/source byte changed')
    result=dict(classification='EVALUATED_ACTUAL_BORN_PRESCRIBED_SOURCE_COTANGENT_AND_INHERITED_CHILD_CURRENT',input_hashes=pins,archives=archives,
        action_parameters=parameters,applications=reports,declared_absolute_field_domain_tolerance=2e-10,
        tolerance_not_a_transferred_homogeneous146_physical_admission_guard=True,
        actual_parent_birth_action_reconstituted_at_preserved_free_q_Pi=True,
        prescribed_wall_and_named_frame_conormal_reactions_retained_not_forced_zero=True,
        source_on_piecewise_Hermite='exact actual birth + two actual root midpoints + two true endpoint Q/coordinateQt germs; C1 interpolant, no fitted shift',
        source_second_germs_are_derivatives_of_declared_interpolant_not_exact_physical_acceleration=True,
        all_fixed_basis_source_high_low_and_independent_current_slots_retained=True,
        full_original_At_Gauss_and_Higgs_rows_audited=True,
        physical_event_native_heat_common_exterior_Gamma2_and_LSZ_not_selected=True,
        next_owned_relation='combine actual prescribed-source endpoint cotangent with full coupled birth formation/energy/gamma(c) rows and action-owned exterior traces; this constrained field-sector continuation does not solve those physical rows',
        error_scope='binary signed constant-stage canonical action and declared C1 actual-owner source interpolation with source first; source/corner and coefficient approximation retained, no action accuracy or outward physical enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),archives=len(archives),pins=len(pins))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.output)
