"""Apply exact84+2 field elimination and solve the original62 geometry rows."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_quadratic_canonical_field_elimination import eliminate_quadratic_canonical_fields,original_field_geometry_indices
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(initial_folder,terminal_folder,output,max_evaluations,tolerance):
    out=ROOT/output;source=ROOT/initial_folder;base=ROOT/terminal_folder
    if out.exists():raise FileExistsError('preserve every exact field-reduced action application')
    refs={}
    def read(folder,name):
        p=folder/name;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(source,'result.json');refs.update(md['input_hashes']);start=read(source,'application.npz')
    if refs[(source/'application.npz').relative_to(ROOT).as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('same reached constitutive checkpoint changed')
    tm=read(base,'result.json');refs.update(tm['input_hashes']);terminal=read(base,'actual_complex_terminal_full_action.npz')
    if refs[(base/'actual_complex_terminal_full_action.npz').relative_to(ROOT).as_posix()]!=tm['archives']['actual_complex_terminal_full_action.npz']['sha256']:
        raise ValueError('original complex terminal changed')
    eta=start['coefficients'];p0=start['canonical_momentum_target'];n=106
    if not np.array_equal(eta[:n],terminal['master_coefficients'][:n])or not np.array_equal(p0,terminal['canonical_momentum']):
        raise ValueError('exact original x/Pi target must remain unchanged')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=phase['coordinates']['lift'];time=terminal['coordinate_time'].item()
    params=tm['action_parameters'];frame=canonical_central_frame(terminal['raw_fields'],rep)
    reference=terminal['master_coefficients'][n:];field,geometry=original_field_geometry_indices()
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**params)
    apply=lambda e:eliminate_quadratic_canonical_fields(e,p0,evaluate,frame,frame_reference=reference)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete original action operands')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    print(json.dumps(dict(stage='exact_original84_field86_saddle',initial_folder=initial_folder.as_posix())),flush=True)
    a0=apply(eta)
    # Independent nonreal displacement of EVERY field variable at fixed
    # geometry validates the actual action polynomial, not just its solve.
    rng=np.random.default_rng(8462146);d=(rng.normal(size=84)+1j*rng.normal(size=84));d*=.03/np.linalg.norm(d)
    shifted=a0['coefficients'].copy();shifted[n+field]+=d;as_=evaluate(shifted)
    H=a0['action']['hessian'][n:,n:];G=a0['action']['gradient'];Gs=as_['gradient']
    affine=Gs[n+field]-G[n+field]-H[np.ix_(field,field)]@d
    quadratic=as_['value']-a0['action']['value']-G[n+field]@d-d@H[np.ix_(field,field)]@d/2
    hessian=as_['hessian'][n+field[:,None],n+field]-H[np.ix_(field,field)]
    controls=dict(field_gradient_affine_relative_max=float(np.max(abs(affine))/max(1.,np.max(abs(G[n+field])),np.max(abs(Gs[n+field])))),
        field_Hessian_constant_relative_max=float(np.max(abs(hessian))/max(1.,np.max(abs(H[np.ix_(field,field)])))),
        field_action_quadratic_relative_error=float(abs(quadratic)/max(1.,abs(as_['value']),abs(a0['action']['value']))))
    if max(controls.values())>2e-9:raise ArithmeticError('actual original84 field polynomial control failed')
    # A literal reduced directional derivative with field rows solved anew.
    dg=(rng.normal(size=62)+1j*rng.normal(size=62));dg/=np.linalg.norm(dg);eps=2e-6
    ep,em=eta.copy(),eta.copy();ep[n+geometry]+=eps*dg;em[n+geometry]-=eps*dg
    ap,am=apply(ep),apply(em);fd=(ap['reduced_geometry_rows']-am['reduced_geometry_rows'])/(2*eps)
    exact=a0['reduced_geometry_Jacobian']@dg
    controls['independent_reduced_Schur_direction_relative_max']=float(np.max(abs(fd-exact))/max(1.,np.max(abs(exact))))
    if controls['independent_reduced_Schur_direction_relative_max']>3e-6:raise ArithmeticError('original geometry Schur derivative control failed')
    save('actual_quadratic_field_and_Schur_controls.npz',dict(field_indices=field,geometry_indices=geometry,
        nonreal_field_direction=d,field_gradient_affine_defect=affine,field_Hessian_constant_defect=hessian,
        field_action_quadratic_defect=np.array(quadratic),nonreal_geometry_direction=dg,epsilon=np.array(eps),
        finite_reduced_geometry_direction=fd,exact_reduced_geometry_direction=exact,
        initial_coefficients=eta,field_solved_initial_coefficients=a0['coefficients']))
    print(json.dumps(dict(stage='exact_original_field_Schur_controls_complete',controls=controls,
        original_field_residual_max=float(np.max(abs(a0['original_field_rows']))),geometry_residual_max=float(np.max(abs(a0['reduced_geometry_rows']))))),flush=True)
    scale=1/np.maximum(np.max(abs(a0['reduced_geometry_Jacobian']),axis=1),1.)
    original=eta.copy();cache={};history=[];invalid=[];evaluations=0
    def realify(z):return np.r_[z.real,z.imag]
    def complexify(x):return x[:62]+1j*x[62:]
    def get(x):
        nonlocal evaluations
        if 'x'in cache and np.array_equal(cache['x'],x):return cache['a']
        e=original.copy();e[n+geometry]=complexify(x);evaluations+=1;a=apply(e)
        cache.update(x=np.asarray(x).copy(),a=a);return a
    def fun(x):
        try:return realify(scale*get(x)['reduced_geometry_rows'])
        except(ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError)as exc:
            invalid.append(dict(evaluation=evaluations,reason=str(exc)));return np.full(124,np.inf)
    def jac(x):
        a=get(x);r=a['original_constitutive_rows'];S=scale[:,None]*a['reduced_geometry_Jacobian']
        record=dict(accepted_iteration=len(history),evaluation=evaluations,fixed_geometry_merit=float(np.linalg.norm(scale*a['reduced_geometry_rows'])),
            original_rows_max=float(np.max(abs(r))),original_momentum_max=float(np.max(abs(r[:n]))),
            original_algebraic_max=float(np.max(abs(r[n:]))),original_field_rows_max=float(np.max(abs(a['original_field_rows']))),
            frame_reaction_max=float(np.max(abs(a['field_frame_reactions']))),
            velocity_algebraic_change_from_original_norm=float(np.linalg.norm(a['coefficients'][n:]-terminal['master_coefficients'][n:])))
        history.append(record)
        save(f'accepted_{len(history)-1:04d}.npz',dict(coefficients=a['coefficients'],original_constitutive_rows=r,
            reduced_geometry_rows=a['reduced_geometry_rows'],reduced_geometry_Jacobian=a['reduced_geometry_Jacobian'],
            field_frame_reactions=a['field_frame_reactions'],original_field_rows=a['original_field_rows'],
            framed_field_rows=a['framed_field_rows']))
        print(json.dumps(dict(stage='original62_geometry_action_solve',**record),sort_keys=True),flush=True)
        return np.block([[S.real,-S.imag],[S.imag,S.real]])
    if max_evaluations:
        initial=realify(eta[n+geometry]);variable_scale=np.maximum(abs(eta[n+geometry]),1.)
        result=least_squares(fun,initial,jac=jac,method='trf',x_scale=np.r_[variable_scale,variable_scale],
            ftol=1e-13,xtol=1e-13,gtol=None,max_nfev=max_evaluations)
        final=get(result.x);optimizer=dict(status=int(result.status),message=str(result.message))
    else:final=a0;optimizer=dict(status=None,message='polynomial elimination and Schur controls only')
    r=final['original_constitutive_rows'];status=('ALL_ORIGINAL_COMPLEX_CONSTITUTIVE_ROWS_TOLERANCE'
        if np.max(abs(r))<=tolerance and np.max(abs(final['framed_field_rows'][-2:]))<=tolerance else 'ORIGINAL_FULL_CONSTITUTIVE_RESIDUAL_REMAINS')
    arrays={key:final[key]for key in('coefficients','canonical_momentum_target','field_indices','geometry_indices','field_frame_saddle',
        'field_frame_reactions','original_field_rows','framed_field_rows','original_constitutive_rows','reduced_geometry_rows',
        'reduced_geometry_Jacobian','implicit_field_geometry_lift','implicit_frame_reaction_geometry_lift','original_frame_reference',
        'literal_generators','named_frame_covectors','literal_gauge_source_compatibility','literal_generator_image',
        'field_hessian_quadratic_identity_defect','field_gradient_affine_identity_defect','implicit_original_field_geometry_rows')}
    arrays.update(raw_fields=P@final['coefficients'],coordinate_time=np.array(time),frame_reactions=final['field_frame_reactions'],
        action_gradient=final['action']['gradient'],action_hessian=final['action']['hessian'],original_terminal_master=terminal['master_coefficients'],
        initial_checkpoint_master=eta,reduced_geometry_row_scale=scale)
    save('application.npz',arrays)
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for p in(Path(__file__),'tests/test_muon_quadratic_canonical_field_elimination.py'):
        p=Path(p);p=p if p.is_absolute()else ROOT/p;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same original reduced action source changed')
    md=dict(classification='EVALUATED_EXACT_QUADRATIC_FIELD86_REDUCTION_AND_ORIGINAL62_COMPLEX_GEOMETRY_CONSTITUTIVE_APPLICATION',
        input_hashes=refs,archives=archives,status=status,history=history,controls=controls,optimizer=optimizer,
        max_evaluations=max_evaluations,reduced_action_evaluations=evaluations,tolerance=tolerance,
        original_rows_max=float(np.max(abs(r))),original_momentum_residual_max=float(np.max(abs(r[:n]))),
        original_algebraic_residual_max=float(np.max(abs(r[n:]))),original_field_rows_max=float(np.max(abs(final['original_field_rows']))),
        field_frame_reaction_max=float(np.max(abs(final['field_frame_reactions']))),
        same_original_fixed_x_and_Pi=True,original_named_frame_reference_changed=False,
        original_rows_or_spectral_directions_removed=0,field_rows_exact_quadratic_elimination=True,
        field_Gauss_rows_retained=True,Schur_uses_both_independent_cross_blocks=True,
        action_parameters=params,lambda_H=rep['scalar_matching']['lambda_H'],surface_gamma_is_retained_unassigned=True,
        complete_physical_gamma_branch_stop_pole_or_Pauli_selected=False,
        error_scope='binary64 original action polynomial field elimination and geometry Schur; convergence checked on all146 original rows, no physical branch/first-hit/Pauli enclosure')
    p=out/'result.json';p.write_text(json.dumps(md,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='exact_original_field_reduced_geometry_complete',status=status,
        original_rows_max=md['original_rows_max'],result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initial-folder',type=Path,default=Path('artifacts/muon_safeguarded_complex_constitutive_20261011/resumed_run_1'))
    p.add_argument('--terminal-folder',type=Path,default=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-evaluations',type=int,default=40)
    p.add_argument('--tolerance',type=float,default=2e-10);a=p.parse_args()
    materialize(a.initial_folder,a.terminal_folder,a.output,a.max_evaluations,a.tolerance)
