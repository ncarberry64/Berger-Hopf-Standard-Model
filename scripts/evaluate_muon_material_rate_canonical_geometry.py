"""Apply exact121+2 material-rate reduction to the original25 geometry rows."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_material_rate_canonical_reduction import fixed_position_material_rate_chart,eliminate_material_rate_quadratic_fields
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(initial_folder,terminal_folder,output,max_iterations,tolerance,control_step=2e-6):
    out=ROOT/output;source=ROOT/initial_folder;base=ROOT/terminal_folder
    if out.exists():raise FileExistsError('preserve every material-rate action application')
    refs={}
    def read(folder,name):
        p=folder/name;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(source,'result.json');refs.update(md['input_hashes']);start=read(source,'application.npz')
    if refs[(source/'application.npz').relative_to(ROOT).as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('same complete initial action changed')
    tm=read(base,'result.json');refs.update(tm['input_hashes']);terminal=read(base,'actual_complex_terminal_full_action.npz')
    if refs[(base/'actual_complex_terminal_full_action.npz').relative_to(ROOT).as_posix()]!=tm['archives']['actual_complex_terminal_full_action.npz']['sha256']:
        raise ValueError('same actual terminal changed')
    eta=start['coefficients'];p0=start['canonical_momentum_target'];n=106;fixed=eta[:n]
    if not np.array_equal(fixed,terminal['master_coefficients'][:n])or not np.array_equal(p0,terminal['canonical_momentum']):
        raise ValueError('same original fixed x/Pi target required')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=phase['coordinates']['lift'];time=terminal['coordinate_time'].item()
    params=tm['action_parameters'];frame=canonical_central_frame(terminal['raw_fields'],rep);reference=terminal['master_coefficients'][n:]
    chart=fixed_position_material_rate_chart((P@eta)[:100]);T=chart['velocity_algebraic_lift'];Ti=chart['velocity_algebraic_inverse'];S=chart['fixed_position_phase_lift']
    f=chart['field_indices'];g=chart['nonlinear_geometry_indices'];original_material=Ti@eta[n:]
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**params)
    def apply(w):
        material=original_material.copy();material[g]=w;candidate=np.r_[fixed,T@material]
        return eliminate_material_rate_quadratic_fields(candidate,p0,evaluate,frame,chart,frame_reference=reference)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split original complete action operands')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    w=original_material[g];print(json.dumps(dict(stage='exact_original_material121_field123_saddle')),flush=True)
    a=apply(w);rng=np.random.default_rng(121252146);df=rng.normal(size=121)+1j*rng.normal(size=121);df*=.03/np.linalg.norm(df)
    e=a['coefficients'].copy();e[n+f]+=df;aa=evaluate(S@e);G=S.T@aa['gradient'];H=S.T@aa['hessian']@S
    first=a['action'];G0=first['gradient'];H0=first['hessian'];D=H0[n:,n:]
    affine=G[n+f]-G0[n+f]-D[np.ix_(f,f)]@df
    hdef=H[n+f[:,None],n+f]-D[np.ix_(f,f)]
    qdef=aa['value']-first['value']-G0[n+f]@df-df@D[np.ix_(f,f)]@df/2
    controls=dict(actual121_gradient_affine_relative_max=float(np.max(abs(affine))/max(1.,np.max(abs(G[n+f])),np.max(abs(G0[n+f])))),
        actual121_Hessian_constant_relative_max=float(np.max(abs(hdef))/max(1.,np.max(abs(D[np.ix_(f,f)])))),
        actual121_action_quadratic_relative_error=float(abs(qdef)/max(1.,abs(aa['value']),abs(first['value']))),
        qdot37_field84_cross_max=float(np.max(abs(D[np.ix_(np.arange(37),f[37:])]))),
        literal_canonical_row_transform_max=float(np.max(abs(a['transformed_original_row_identity']))))
    if max(controls[k]for k in controls if k.endswith('relative_max')or k.endswith('relative_error'))>2e-9:
        raise ArithmeticError('original121 material-rate quadratic action control failed')
    dg=rng.normal(size=25)+1j*rng.normal(size=25);dg/=np.linalg.norm(dg);eps=control_step
    ap,am=apply(w+eps*dg),apply(w-eps*dg);fd=(ap['reduced_geometry_rows']-am['reduced_geometry_rows'])/(2*eps)
    exact=a['reduced_geometry_Jacobian']@dg
    controls['independent_material25_Schur_direction_relative_max']=float(np.max(abs(fd-exact))/max(1.,np.max(abs(exact))))
    save('actual_material_quadratic_controls.npz',dict(velocity_algebraic_lift=T,velocity_algebraic_inverse=Ti,
        material_field_indices=f,material_geometry_indices=g,nonreal_121_direction=df,field_affine_identity_defect=affine,
        field_Hessian_identity_defect=hdef,field_quadratic_action_defect=np.array(qdef),nonreal_25_direction=dg,
        finite_material_geometry_direction=fd,exact_material_geometry_direction=exact,epsilon=np.array(eps)))
    print(json.dumps(dict(stage='original121_material25_controls_complete',controls=controls,
        all_original146_rows_max=float(np.max(abs(a['original_coordinate_constitutive_rows']))),
        control_step=eps,quadratic123_saddle_condition=float(np.linalg.cond(a['field_frame_saddle'])),
        finite_direction_max=float(np.max(abs(fd))),exact_direction_max=float(np.max(abs(exact))))),flush=True)
    if controls['independent_material25_Schur_direction_relative_max']>3e-6:raise ArithmeticError('original material25 Schur derivative failed')
    scale=1/np.maximum(np.max(abs(a['reduced_geometry_Jacobian']),axis=1),1.);history=[];status='ITERATION_LIMIT'
    for iteration in range(max_iterations+1):
        r=a['original_coordinate_constitutive_rows'];R=a['reduced_geometry_rows'];J=a['reduced_geometry_Jacobian'];merit=float(np.linalg.norm(scale*R))
        record=dict(iteration=iteration,fixed_material_geometry_merit=merit,
            original_rows_max=float(np.max(abs(r))),original_momentum_max=float(np.max(abs(r[:n]))),
            original_algebraic_max=float(np.max(abs(r[n:]))),
            transformed121_quadratic_rows_max=float(np.max(abs(a['original_field_rows']))),
            frame_reaction_max=float(np.max(abs(a['field_frame_reactions']))),
            velocity_algebraic_change_from_original_norm=float(np.linalg.norm(a['original_coefficients'][n:]-terminal['master_coefficients'][n:])))
        history.append(record)
        save(f'iteration_{iteration:04d}.npz',dict(original_coefficients=a['original_coefficients'],material_coefficients=a['coefficients'],
            original_constitutive_rows=r,material25_rows=R,material25_Schur=J,
            field_frame_reactions=a['field_frame_reactions'],all121_field_rows=a['original_field_rows'],framed_field_rows=a['framed_field_rows']))
        print(json.dumps(dict(stage='original25_material_geometry_Newton',**record),sort_keys=True),flush=True)
        if np.max(abs(r))<=tolerance and np.max(abs(a['framed_field_rows'][-2:]))<=tolerance:
            status='ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE';break
        if iteration==max_iterations:break
        col=1/np.maximum(np.max(abs(scale[:,None]*J),axis=0),np.finfo(float).tiny)
        B=scale[:,None]*J*col[None,:];dw=col*np.linalg.solve(B,-scale*R)
        record.update(balanced_material25_condition_number=float(np.linalg.cond(B)),material25_Newton_step_norm=float(np.linalg.norm(dw)),
            original_reduced_linearized_rows_max=float(np.max(abs(J@dw+R))))
        accepted=False;trials=[]
        for k in range(20):
            damping=2.**(-k);wt=w+damping*dw
            try:
                at=apply(wt);new=float(np.linalg.norm(scale*at['reduced_geometry_rows']));good=np.isfinite(new)and new<merit
            except(ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError,ArithmeticError):new=None;good=False
            trials.append(dict(damping=damping,material_geometry_merit=new,accepted=bool(good)))
            if good:accepted=True;break
        record['trials']=trials
        if not accepted:status='MATERIAL25_LINE_SEARCH_STALL';break
        w,a=wt,at
    r=a['original_coordinate_constitutive_rows'];arrays={key:a[key]for key in('field_indices','geometry_indices','field_frame_saddle',
        'original_field_rows','framed_field_rows','reduced_geometry_rows','reduced_geometry_Jacobian','implicit_field_geometry_lift',
        'implicit_frame_reaction_geometry_lift','transformed_original_row_identity','original_literal_generator_image',
        'original_literal_gauge_source_compatibility','field_hessian_quadratic_identity_defect','field_gradient_affine_identity_defect')}
    arrays.update(coefficients=a['original_coefficients'],raw_fields=P@a['original_coefficients'],canonical_momentum_target=p0,
        original_terminal_master=terminal['master_coefficients'],original_frame_reference=reference,frame_reactions=a['field_frame_reactions'],
        original_constitutive_rows=r,action_gradient=a['original_action']['gradient'],action_hessian=a['original_action']['hessian'],
        material_coefficients=a['coefficients'],material_canonical_target=a['canonical_momentum_target'],coordinate_time=np.array(time),
        velocity_algebraic_lift=T,velocity_algebraic_inverse=Ti,material25_row_scale=scale,initial_checkpoint_master=eta)
    save('application.npz',arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_material_rate_canonical_reduction.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('original material action pins changed')
    result=dict(classification='EVALUATED_EXACT_MATERIAL121_QUADRATIC_FRAME123_AND_ORIGINAL25_GEOMETRY_ACTION',input_hashes=refs,
        archives=archives,status=status,history=history,controls=controls,control_step=control_step,max_iterations=max_iterations,tolerance=tolerance,
        original_rows_max=float(np.max(abs(r))),original_momentum_residual_max=float(np.max(abs(r[:n]))),
        original_algebraic_residual_max=float(np.max(abs(r[n:]))),transformed121_field_rows_max=float(np.max(abs(a['original_field_rows']))),
        field_frame_reaction_max=float(np.max(abs(a['field_frame_reactions']))),
        all_original146_rows_retained=True,same_fixed_x_and_original_Pi=True,original_frame_reference_reset=False,
        material_transform_used_only_at_fixed_x=True,canonical_x_force_without_transform_contacts_used=False,
        returned_original_coordinates_for_canonical_continuation=True,original_rows_or_spectral_directions_removed=0,
        action_parameters=params,lambda_H=rep['scalar_matching']['lambda_H'],surface_gamma_is_retained_unassigned=True,
        complete_physical_gamma_branch_first_hit_Pauli_or_error_bound=False,
        error_scope='binary64 literal material-rate polynomial elimination with original canonical row checks; no physical branch or stop selection')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='original_material25_complete',status=status,original_rows_max=result['original_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initial-folder',type=Path,default=Path('artifacts/muon_reduced_complex_canonical_geometry_20261011/run_1'))
    p.add_argument('--terminal-folder',type=Path,default=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-iterations',type=int,default=12)
    p.add_argument('--tolerance',type=float,default=2e-10);p.add_argument('--control-step',type=float,default=2e-6);a=p.parse_args()
    materialize(a.initial_folder,a.terminal_folder,a.output,a.max_iterations,a.tolerance,a.control_step)
