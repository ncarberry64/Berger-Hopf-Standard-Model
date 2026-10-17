"""Continue the actual full302/original226 nonlinear reset equations."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_coupled_reset_continuation import coupled_reset_application,central_reset_Ward_rows,complex_reset_chart
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(previous,output,max_iterations,tolerance):
    source=ROOT/previous;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every nonlinear coupled reset continuation')
    refs={}
    def read(name):
        p=source/name;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read('result.json');refs.update(md['input_hashes']);base=read('full_coupled_original_reset.npz')
    if md.get('original226_Newton_probe',{}).get('accepted_decrease_only_not_compatible'):
        name=next(x for x in md['archives']if x.startswith('original226_probe_damping_'))
        start=read(name);raw=start['raw_pair']
    else:
        start=read('application.npz');raw=start['raw_pair']
    reference=base['reference_pair'];R=base['master_lift'];phase,_=retained_input('outgoing',refs);rep=phase['representation'];params=md['action_parameters']
    input_path=next(Path(x)for x in refs if x.endswith('true_phase_projection_inputs.npz'))
    b=(ROOT/input_path).read_bytes();refs[input_path.as_posix()]=sha256(b).hexdigest()
    with np.load(ROOT/input_path,allow_pickle=False)as z:weights=z['state_weights'].copy();norm=z['normalization_coordinates'].copy()
    mw=abs(R.T)@np.tile(np.r_[weights,np.ones(170)],2)
    evaluate=lambda x,j=True:coupled_reset_application(x,reference,rep,weights,norm,action_parameters=params,compute_jacobian=j)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete reset checkpoints')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    a=evaluate(raw);ward=central_reset_Ward_rows(a,raw,rep);row_scale=1/np.maximum(np.max(abs(a['jacobian']/mw[None,:]),axis=1),1.)
    history=[];status='ITERATION_LIMIT';initial=raw.copy()
    for iteration in range(max_iterations+1):
        r=a['residual'];J=a['jacobian'];ward=central_reset_Ward_rows(a,raw,rep);merit=float(np.linalg.norm(row_scale*r))
        record=dict(iteration=iteration,all_original226_rows_max=float(np.max(abs(r))),fixed_scaled_merit=merit,
            incoming_constraints_max=float(np.max(abs(r[a['groups']['incoming_constraints']]))),
            child_constraints_max=float(np.max(abs(r[a['groups']['child_constraints']]))),
            named_Ward_identity_max=float(np.max(abs(ward['original_nonlinear_identity']))),
            full302_original_phase_rows_max=float(np.max(abs(a['projection']['original_phase_rows']))),
            full302_transpose_adjoint_rows_max=float(np.max(abs(a['projection']['analytic_adjoint_rows']))),
            chart=complex_reset_chart(raw));history.append(record)
        save(f'iteration_{iteration:04d}.npz',dict(raw_pair=raw,reference_pair=reference,master_lift=R,
            original226_rows=r,original226_Jacobian=J,full_master_gradient=a['action']['gradient'],
            full_master_Hessian=a['action']['hessian'],area_parameter_source=a['area_parameter_source'],
            Ward_rows=ward['rows'],Ward_identity=ward['original_nonlinear_identity'],
            dependent_original_rows=ward['dependent_original_rows'],independent_original_rows=ward['independent_original_rows'],
            row_scale=row_scale,coordinate_weights=mw,phase_lift=a['projection']['phase_lift'],
            frame_reactions=a['projection']['frame_reactions'],original_phase_rows=a['projection']['original_phase_rows']))
        print(json.dumps(dict(stage='continued_original226_full_phase_reset',**record),sort_keys=True),flush=True)
        if np.max(abs(r))<=tolerance:status='ALL_ORIGINAL226_RESET_ROWS_TOLERANCE';break
        if iteration==max_iterations:break
        if np.max(abs(ward['original_nonlinear_identity']))>2e-8:
            status='NAMED_NONLINEAR_WARD_IDENTITY_CONTROL_FAILED';break
        keep=ward['independent_original_rows'];M=row_scale[keep,None]*J[keep]/mw[None,:]
        correction,residual,rank,singular=np.linalg.lstsq(M,-row_scale[keep]*r[keep],rcond=None)
        if rank!=224:record['rank']=int(rank);status='NAMED224_ROW_RANGE_UNRESOLVED';break
        correction=correction/mw;linear=J@correction+r
        record.update(independent_rank=int(rank),correction_norm=float(np.linalg.norm(correction)),
            all_original_linearized_rows_max=float(np.max(abs(linear))),dependent_linearized_rows_max=float(np.max(abs(linear[ward['dependent_original_rows']]))))
        accepted=False;record['trials']=[];eta=R.T@raw.reshape(-1)
        for k in range(14):
            damping=2.**(-k);trialraw=(R@(eta+damping*correction)).reshape(2,268)
            try:
                chart=complex_reset_chart(trialraw);trial=evaluate(trialraw,False);new=float(np.linalg.norm(row_scale*trial['residual']))
                trialward=central_reset_Ward_rows(trial,trialraw,rep)
                good=np.isfinite(new)and new<merit and np.max(abs(trialward['original_nonlinear_identity']))<=2e-8
                rec=dict(damping=damping,merit=new,original_rows_max=float(np.max(abs(trial['residual']))),
                    named_Ward_identity_max=float(np.max(abs(trialward['original_nonlinear_identity']))),accepted=bool(good))
            except (ValueError,FloatingPointError,OverflowError,np.linalg.LinAlgError)as error:
                good=False;rec=dict(damping=damping,accepted=False,error=str(error))
            record['trials'].append(rec)
            if good:
                save(f'accepted_{iteration:04d}.npz',dict(raw_pair=trialraw,reference_pair=reference,original226_rows=trial['residual'],
                    original_master_correction=correction,all_original_linearized_rows=linear,
                    Ward_rows=trialward['rows'],Ward_identity=trialward['original_nonlinear_identity']))
                raw=trialraw;a=evaluate(raw);accepted=True;break
        if not accepted:status='ORIGINAL226_LINE_SEARCH_STALL';break
    save('application.npz',dict(raw_pair=raw,reference_pair=reference,master_lift=R,
        original226_rows=a['residual'],original226_Jacobian=a['jacobian'],full_master_gradient=a['action']['gradient'],
        full_master_Hessian=a['action']['hessian'],area_parameter_source=a['area_parameter_source'],
        Ward_rows=ward['rows'],Ward_identity=ward['original_nonlinear_identity'],row_scale=row_scale,coordinate_weights=mw,
        parent_energy=np.array(a['action']['parent']['value']),frame_reactions=a['projection']['frame_reactions'],
        original_phase_rows=a['projection']['original_phase_rows']))
    # Resume schema is explicit and does not reconstruct a lost optimization.
    save('full_coupled_original_reset.npz',dict(reference_pair=reference,master_lift=R))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same coupled reset action source changed')
    result=dict(classification='EVALUATED_CONTINUED_COMPLEX_FULL_PHASE_ORIGINAL226_RESET_EQUATIONS',input_hashes=refs,archives=archives,
        status=status,history=history,tolerance=tolerance,original226_rows_max=float(np.max(abs(a['residual']))),
        raw_state_change_from_resume_norm=float(np.linalg.norm(raw-initial)),action_parameters=params,
        groups=a['groups'],named_dependent_original_rows=ward['dependent_original_rows'].tolist(),
        all_original226_rows_checked=True,numerical_singular_vectors_used_for_row_selection=False,
        additional_rank_defect_discarded=False,full_Lyy_and_true302_frame_response_retained=True,
        derivative_scope='binary full536 action twojet; single full-Hessian centered directional third contraction and exact traceDB; no derivative enclosure',
        gamma_law=md['gamma_law'],parent_canonical_exterior_or_physical_reference_first_hit_selected=False,
        error_scope='same held-snapshot coupled reset numerical continuation; original equations and exact named central Ward relations retained, no physical formation or anomaly claim')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='continued_coupled_original_reset_complete',status=status,original_rows_max=result['original226_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,
        default=Path('artifacts/muon_coupled_complex_two_arm_reset_20261012/run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-iterations',type=int,default=12)
    p.add_argument('--tolerance',type=float,default=2e-10);a=p.parse_args();materialize(a.previous,a.output,a.max_iterations,a.tolerance)
