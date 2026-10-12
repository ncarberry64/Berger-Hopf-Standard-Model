"""Continue the SAME material25 action solve from its saved nonlinear point."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_material_rate_canonical_reduction import fixed_position_material_rate_chart,eliminate_material_rate_quadratic_fields
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(previous,output,max_iterations,tolerance):
    out=ROOT/output;source=ROOT/previous
    if out.exists():raise FileExistsError('preserve every continued material action solve')
    refs={}
    def read(path):
        p=ROOT/path;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(previous/'result.json');refs.update(md['input_hashes']);saved=read(previous/'application.npz')
    if refs[(previous/'application.npz').as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('saved nonlinear material point changed')
    # This same fixed field/qdot anchor preserves the earlier polynomial
    # evaluation chart. The saved nonlinear coordinates carry progress;
    # no ancestor optimization or derivative control is rerun.
    anchor_path=Path('artifacts/muon_reduced_complex_canonical_geometry_20261011/run_1/application.npz')
    anchor=read(anchor_path)
    terminal=read('artifacts/muon_holomorphic_child_terminal_20261011/run_2/actual_complex_terminal_full_action.npz')
    if not np.array_equal(saved['canonical_momentum_target'],anchor['canonical_momentum_target'])or not np.array_equal(saved['coefficients'][:106],anchor['coefficients'][:106]):
        raise ValueError('same original position and Pi must survive continuation')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=phase['coordinates']['lift'];n=106
    eta=anchor['coefficients'];p0=anchor['canonical_momentum_target'];time=saved['coordinate_time'].item()
    chart=fixed_position_material_rate_chart((P@eta)[:100]);T=chart['velocity_algebraic_lift'];Ti=chart['velocity_algebraic_inverse'];g=chart['nonlinear_geometry_indices']
    if not np.array_equal(T,saved['velocity_algebraic_lift'])or not np.array_equal(Ti,saved['velocity_algebraic_inverse']):raise ValueError('fixed material chart changed')
    material_anchor=Ti@eta[n:];w=saved['material_coefficients'][n+g].copy();scale=saved['material25_row_scale']
    frame=canonical_central_frame(terminal['raw_fields'],rep);reference=terminal['master_coefficients'][n:];params=md['action_parameters']
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**params)
    def apply(w):
        c=material_anchor.copy();c[g]=w
        return eliminate_material_rate_quadratic_fields(np.r_[eta[:n],T@c],p0,evaluate,frame,chart,frame_reference=reference)
    def admissibility(a):
        raw=P@a['original_coefficients'];q,v,m,d,dr,wall,C=_geometry_variables(raw[:100],differentiate=False);F=_fields(12,q,v,m,wall)
        U=F['C'].value*(dr.value+F['beta'].value)/F['N'].value
        response=a['original_action']['response_chart'];av=response['coefficients']
        return dict(material_normal_chart_abs_delta=float(abs(d.value)),holomorphic_wall_velocity_abs_U=float(abs(U)),
            anchored_response_monotonicity_margin=float(1-2*abs(av[0])-6*abs(av[1])),
            implicit_response_residual_max=float(np.max(abs(response['implicit_residual']))),
            induced_lapse_real=float(a['original_action']['induced_lapse'].real),
            induced_lapse_imag=float(a['original_action']['induced_lapse'].imag),
            FR_denominator_real=float(a['original_action']['FR_denominator'].real),
            FR_denominator_imag=float(a['original_action']['FR_denominator'].imag))
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete original action rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    a=apply(w);resume_difference=a['original_coordinate_constitutive_rows']-saved['original_constitutive_rows']
    save('resume_point_control.npz',dict(saved_nonlinear_material_coordinates=w,
        saved_original_rows=saved['original_constitutive_rows'],reconstructed_original_rows=a['original_coordinate_constitutive_rows'],
        original_row_resume_difference=resume_difference))
    print(json.dumps(dict(stage='same_material25_saved_point_resume',original_row_reconstruction_max=float(np.max(abs(resume_difference))),
        original_rows_max=float(np.max(abs(a['original_coordinate_constitutive_rows']))),admissibility=admissibility(a))),flush=True)
    history=[];status='ITERATION_LIMIT'
    for i in range(max_iterations+1):
        r=a['original_coordinate_constitutive_rows'];R=a['reduced_geometry_rows'];J=a['reduced_geometry_Jacobian'];merit=float(np.linalg.norm(scale*R))
        rec=dict(iteration=i,fixed_material_geometry_merit=merit,original_rows_max=float(np.max(abs(r))),
            original_momentum_max=float(np.max(abs(r[:n]))),original_algebraic_max=float(np.max(abs(r[n:]))),
            transformed121_quadratic_rows_max=float(np.max(abs(a['original_field_rows']))),
            original84_field_rows_max=float(np.max(abs(r[np.r_[38:106,130:146]]))),
            velocity_algebraic_change_from_original_norm=float(np.linalg.norm(a['original_coefficients'][n:]-terminal['master_coefficients'][n:])),
            admissibility=admissibility(a))
        history.append(rec)
        save(f'iteration_{i:04d}.npz',dict(original_coefficients=a['original_coefficients'],material_coefficients=a['coefficients'],
            nonlinear_material_coordinates=w,original_constitutive_rows=r,material25_rows=R,material25_Schur=J,
            field_frame_reactions=a['field_frame_reactions'],all121_quadratic_rows=a['original_field_rows']))
        print(json.dumps(dict(stage='continued_original25_material_Newton',**rec),sort_keys=True),flush=True)
        if np.max(abs(r))<=tolerance and np.max(abs(a['framed_field_rows'][-2:]))<=tolerance:
            status='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE';break
        if i==max_iterations:break
        col=1/np.maximum(np.max(abs(scale[:,None]*J),axis=0),np.finfo(float).tiny)
        B=scale[:,None]*J*col[None,:];dw=col*np.linalg.solve(B,-scale*R)
        rec.update(balanced_material25_condition_number=float(np.linalg.cond(B)),material25_Newton_step_norm=float(np.linalg.norm(dw)),
            reduced_linearized_rows_max=float(np.max(abs(J@dw+R))))
        accepted=False;trials=[]
        for j in range(20):
            damping=2.**(-j);wt=w+damping*dw
            try:
                at=apply(wt);new=float(np.linalg.norm(scale*at['reduced_geometry_rows']));good=np.isfinite(new)and new<merit
            except(ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError,ArithmeticError):new=None;good=False
            trials.append(dict(damping=damping,material_geometry_merit=new,accepted=bool(good)))
            if good:accepted=True;break
        rec['trials']=trials
        if not accepted:status='MATERIAL25_LINE_SEARCH_STALL';break
        w,a=wt,at
    r=a['original_coordinate_constitutive_rows'];arrays={key:a[key]for key in('field_indices','geometry_indices','field_frame_saddle',
        'original_field_rows','framed_field_rows','reduced_geometry_rows','reduced_geometry_Jacobian','implicit_field_geometry_lift',
        'implicit_frame_reaction_geometry_lift','transformed_original_row_identity','original_literal_generator_image','original_literal_gauge_source_compatibility')}
    arrays.update(coefficients=a['original_coefficients'],raw_fields=P@a['original_coefficients'],canonical_momentum_target=p0,
        original_terminal_master=terminal['master_coefficients'],original_frame_reference=reference,frame_reactions=a['field_frame_reactions'],
        original_constitutive_rows=r,action_gradient=a['original_action']['gradient'],action_hessian=a['original_action']['hessian'],
        material_coefficients=a['coefficients'],material_canonical_target=a['canonical_momentum_target'],nonlinear_material_coordinates=w,
        coordinate_time=np.array(time),velocity_algebraic_lift=T,velocity_algebraic_inverse=Ti,material25_row_scale=scale)
    save('application.npz',arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same original material source changed')
    result=dict(classification='CONTINUED_SAME_FIXED_POSITION_MATERIAL25_ORIGINAL_CANONICAL_ACTION',input_hashes=refs,archives=archives,
        status=status,history=history,max_iterations=max_iterations,tolerance=tolerance,
        inherited_controls=md.get('controls',md.get('inherited_controls')),controls_scope='retained original-run controls, no new derivative enclosure inferred',
        original_row_resume_reconstruction_max=float(np.max(abs(resume_difference))),original_rows_max=float(np.max(abs(r))),
        original_momentum_residual_max=float(np.max(abs(r[:n]))),original_algebraic_residual_max=float(np.max(abs(r[n:]))),
        original84_field_rows_max=float(np.max(abs(r[np.r_[38:106,130:146]]))),final_admissibility=admissibility(a),
        same_original_x_Pi_frame_and_numerical_merit=True,ancestor_optimization_or_controls_rerun=False,
        material_chart_x_force_without_contacts_used=False,all_original146_rows_retained=True,
        action_parameters=params,lambda_H=rep['scalar_matching']['lambda_H'],surface_gamma_is_retained_unassigned=True,
        complete_physical_gamma_branch_first_hit_Pauli_or_error_bound=False,
        error_scope='binary64 continued literal25 material action with original146 checks and local nonreal chart admissibility; no physical branch/stop bound')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='continued_material25_complete',status=status,original_rows_max=result['original_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-iterations',type=int,default=24)
    p.add_argument('--tolerance',type=float,default=2e-10);a=p.parse_args();materialize(a.previous,a.output,a.max_iterations,a.tolerance)
