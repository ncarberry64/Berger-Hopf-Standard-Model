"""Retain the actual source cotangent at the inherited child coefficient corner."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_holomorphic_n1_magnetic_action import original_named_wall_lift,complete_gauge_wall_constraints,original_field_permutation
from bhsm.interface.muon_nonlinear_chronological_n0_action import chronological_n0_field_lifts
from bhsm.interface.muon_holomorphic_magnetic_birth_matching import signed_field_face_reconstruction
from bhsm.interface.muon_holomorphic_magnetic_birth_source_contacts import magnetic_birth_source_contacts
from bhsm.interface.muon_holomorphic_magnetic_inherited_cauchy import actual_owner_piecewise_source_germ,signed_field_face_source_first
from bhsm.interface.muon_holomorphic_magnetic_source_faces import signed_field_face_source_complete,actual_owner_one_sided_source_germ
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve actual coefficient-corner return')
    pins={};archives={}
    def read(p,h=None):
        p=ROOT/p if not p.is_absolute()else p;b=p.read_bytes();digest=sha256(b).hexdigest();pins[p.relative_to(ROOT).as_posix()]=digest
        if h is not None and h!=digest:raise ValueError('same source/action pin differs')
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    source=ROOT/'artifacts/muon_holomorphic_magnetic_inherited_cauchy_20261012/run_1';sm=read(source/'result.json')
    pins.update(sm['input_hashes']);phase=load_profile_preserving_phase('artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=ROOT)
    pins.update(phase['input_hashes']);rep=phase['representation'];ids=original_field_permutation(rep);lifts=chronological_n0_field_lifts(rep,ids)
    L=np.kron(original_named_wall_lift(rep,ids),np.eye(4));C=complete_gauge_wall_constraints(lifts,4)['constraint'];F=np.kron(lifts['frame_rows'],np.eye(4))
    reports={};data={}
    for case in('normal_basis','area_source'):
        a=read(source/f'{case}_inherited_on_source_canonical_response.npz',sm['archives'][f'{case}_inherited_on_source_canonical_response.npz']['sha256'])
        b=read(source/f'{case}_actual_birth_reconstitution_and_source_contacts.npz',sm['archives'][f'{case}_actual_birth_reconstitution_and_source_contacts.npz']['sha256'])
        old=ROOT/f'artifacts/muon_holomorphic_n1_magnetic_action_20261012/outgoing_{case}_run_1';om=read(old/'result.json')
        get=lambda name:read(old/name,om['archives'][name]['sha256'])
        forms=[get(f'stage_{j}_original_signed_forms.npz')for j in range(2)];first=[]
        for j in range(2):
            d=[get(f'stage_{j}_original_signed_forms_first_{label}.npz')for label in('high','low')]
            first.append({n:np.array([v[n]for v in d])for n in('K','M','B_forward','B_reverse')})
        sources=[dict(Q=b['actual_Q'][j],Q_coordinate_time=b['actual_Qt'][j],Q_first=b['actual_Q_first'][j],
            Q_coordinate_time_first=b['actual_Qt_first'][j])for j in range(5)]
        oldprefix=get('actual_zero_Cauchy_magnetic_prefix.npz');total=sum(oldprefix['future_coordinate_steps'])
        germ=actual_owner_piecewise_source_germ(.5,b['source_knots'],sources,total)
        dgerm=actual_owner_piecewise_source_germ(.5,b['source_knots'],sources,total,first=True)
        S=a['original_interior_field_lift'];z=a['stage_final_reduced_states'][0];dz=a['stage_final_reduced_states_first'][0]
        germs=[actual_owner_one_sided_source_germ(.5,b['source_knots'],sources,total,side=side)for side in('left','right')]
        dgerms=[actual_owner_one_sided_source_germ(.5,b['source_knots'],sources,total,first=True,side=side)for side in('left','right')]
        faces=[signed_field_face_reconstruction(f,S,L,wg,z,48)for f,wg in zip(forms,germs)]
        contacts=magnetic_birth_source_contacts(faces[0],faces[1],C,S,L,F,germ[0],germ[0])
        derivative=[signed_field_face_source_complete(f,df,S,L,wg,dwg,dz,face,48)for f,df,wg,dwg,face in zip(forms,first,germs,dgerms,faces)]
        work=[]
        for k in range(2):
            dq=L@dgerm[0][k].reshape(80,3)
            work.append(dq.T@contacts['momentum_jump']+(L@germ[0].reshape(80,3)).T@
                (derivative[0]['canonical_momentum_first'][k]-derivative[1]['canonical_momentum_first'][k]))
        contacts.update(corner_source_cotangent_first=np.array(work),corner_source_Q=germ[0],corner_source_Q_coordinate_rate=germ[1],
            source_first_dynamic_value_jump=(derivative[1]['total_field_first']-derivative[0]['total_field_first'])[:,64:],
            source_first_free_momentum_jump=np.einsum('af,kfs->kas',S[:,48:].T,
                derivative[1]['canonical_momentum_first']-derivative[0]['canonical_momentum_first']),
            **{'left_'+k:v for k,v in faces[0].items()if isinstance(v,np.ndarray)},
            **{'right_'+k:v for k,v in faces[1].items()if isinstance(v,np.ndarray)})
        # Root's weak-action consumer needs actual source-on endpoints and
        # both coefficient-corner faces, not a quadrature point proxy.
        named=dict(named_constraint=C,original_interior_field_lift=S,wall_source_lift=L,named_frame=F)
        faces_to_export=[('corner_left_',0,.5,z,dz),('corner_right_',1,.5,z,dz),
            ('initial_',0,0.,a['initial_reduced_canonical_state'],a['initial_reduced_canonical_state_first']),
            ('final_',1,1.,a['final_reduced_canonical_state'],a['final_reduced_canonical_state_first'])]
        for pre,j,sigma,zz,dzz in faces_to_export:
            side='left'if pre in('corner_left_','final_')else'right'
            wg=actual_owner_one_sided_source_germ(sigma,b['source_knots'],sources,total,side=side)
            dwg=actual_owner_one_sided_source_germ(sigma,b['source_knots'],sources,total,first=True,side=side)
            fa=signed_field_face_reconstruction(forms[j],S,L,wg,zz,48)
            da=signed_field_face_source_complete(forms[j],first[j],S,L,wg,dwg,dzz,fa,48)
            for key in('total_field','total_coordinate_rate','canonical_momentum','original_action_force','canonical_momentum_time'):
                named[pre+key]=fa[key]
            for key in('total_field_first','total_coordinate_rate_first','canonical_momentum_first'):
                named[pre+key]=da[key]
            named[pre+'source_Q']=wg[0];named[pre+'source_Q_coordinate_rate']=wg[1]
            named[pre+'source_Q_coordinate_second']=wg[2]
            named[pre+'source_first_original_rows']=da['original_source_first_Gauss_and_momentum_rows']
            named[pre+'source_first_original_time_rows']=da['original_time_Gauss_and_momentum_first_rows']
        contacts.update(named)
        data[case]=contacts
        reports[case]=dict(source_cotangent_norm=float(np.linalg.norm(contacts['prescribed_source_action_cotangent'])),
            source_cotangent_first_norms=[float(np.linalg.norm(v))for v in work],
            full_momentum_jump_norm=float(np.linalg.norm(contacts['momentum_jump'])),
            free_momentum_jump_max=float(np.max(abs(contacts['momentum_full_free_projection']))),
            named_constraint_range_defect_max=float(np.max(abs(contacts['momentum_named_constraint_range_defect']))),
            source_At_Gauss_pairing_max=float(np.max(abs(contacts['source_At_Gauss_pairing']))),
            full_minus_source_work_max=float(np.max(abs(contacts['full_minus_source_action_cotangent']))),
            source_first_dynamic_value_jump_max=float(np.max(abs(contacts['source_first_dynamic_value_jump']))),
            source_first_free_momentum_jump_max=float(np.max(abs(contacts['source_first_free_momentum_jump']))))
        reports[case].update(birth_initial_algebraic_At_source_first_value_jump_max=float(np.max(abs(b['source_first_inherited_value_jump'][:,:64]))),
            birth_initial_dynamic_source_first_value_jump_max=float(np.max(abs(b['source_first_inherited_value_jump'][:,64:]))))
    for n,m in sorted(sys.modules.items()):
        p=getattr(m,'__file__',None)
        if n.startswith('bhsm.')and p:
            p=Path(p)
            if p.is_relative_to(ROOT):pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    pins['tests/test_muon_holomorphic_magnetic_source_faces.py']=sha256((ROOT/'tests/test_muon_holomorphic_magnetic_source_faces.py').read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in pins.items()):raise ValueError('actual coefficient/source byte changed')
    out.mkdir(parents=True)
    for case,a in data.items():
        p=out/f'{case}_actual_source_corner.npz';_compressed_npz(p,a);archives[p.name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    result=dict(classification='EVALUATED_INHERITED_MAGNETIC_COEFFICIENT_CORNER_SOURCE_COTANGENT',input_hashes=pins,archives=archives,
        applications=reports,sigma=.5,source_value_and_rate_from_same_true_endpoint_germ=True,
        free_canonical_state_continuity_not_full_wall_momentum_continuity=True,
        source_cotangent='Q(.5)^T L^T (Pi_left-Pi_right), original Lorentz action; continued weak cotangent is -i times this',
        source_second_not_used_for_cotangent_but_used_for_complete_declared_cell_At_rate=True,
        initial_final_corner_left_corner_right_full_field_rate_momentum_and_first_germs_exported=True,
        initial_and_final_face_coefficients_are_child_stage_0_and_1_not_relabelled_true_event_actions=True,
        algebraic_At_source_first_jump_is_not_dynamic_reset_trace_failure=True,
        absolute_field_domain_tolerance_not_a_transferred_original146_physical_guard=True,
        source_cotangent_not_integrated_Qdot_traction_energy_work=True,
        held_stage_coefficient_corner_not_a_new_physical_stop_or_birth=True,
        left_and_right_corner_rates_use_their_own_one_sided_source_second_germ=True,
        earlier_run_1_2_left_rate_used_right_second_source_comparison_only=True,
        no_extra_solve_or_precision_campaign=True,
        scope='actual distributional source return of the declared piecewise-constant signed child action, with source-first and all free/wall/frame/H/At images retained; no physical pole/normalization inference')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(p.read_bytes()).hexdigest(),applications=reports,pins=len(pins))),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();materialize(a.output)
