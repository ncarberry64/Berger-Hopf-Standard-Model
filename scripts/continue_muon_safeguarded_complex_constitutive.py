"""Resume the preserved all148 original canonical residual application."""
from hashlib import sha256
import argparse,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_safeguarded_complex_constitutive import safeguarded_complex_constitutive
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(previous,terminal,output,*,max_evaluations):
    old=ROOT/previous; original=ROOT/terminal; out=ROOT/output
    if out.exists():raise FileExistsError('preserve all accepted residual applications')
    receipt=json.loads((old/'result.json').read_bytes());refs=dict(receipt['input_hashes'])
    for rel,h in refs.items():
        if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:
            raise ValueError('same canonical/source owner changed: '+rel)
    for folder,names in ((old,('result.json','application.npz')),
                         (original,('result.json','actual_complex_terminal_full_action.npz'))):
        for name in names:
            p=folder/name;refs[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    if refs[(old/'application.npz').relative_to(ROOT).as_posix()]!=receipt['archives']['application.npz']['sha256']:
        raise ValueError('saved original residual state changed')
    with np.load(old/'application.npz',allow_pickle=False)as a: previous_arrays={k:a[k].copy()for k in a.files}
    with np.load(original/'actual_complex_terminal_full_action.npz',allow_pickle=False)as a: data={k:a[k].copy()for k in a.files}
    if not np.array_equal(previous_arrays['coefficients'][:106],data['master_coefficients'][:106]):
        raise ValueError('same fixed position required')
    if not np.array_equal(previous_arrays['canonical_momentum_target'],data['canonical_momentum']):
        raise ValueError('same full-action momentum target required')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=data['coordinate_lift']
    time=data['coordinate_time'].item();parameters=receipt['action_parameters']
    frame=canonical_central_frame(data['raw_fields'],rep)
    frame_reference_defect=frame['named_frame_covectors']@(previous_arrays['coefficients'][106:]-data['master_coefficients'][106:])
    if np.max(abs(frame_reference_defect))>1e-12:
        raise ValueError('saved named temporal frame changed')
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time,phase['arrays']['initial_pair'],
        phase['arrays']['reference_pair'],rep,**parameters)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def checkpoint(record,e,rho,a,r,f,J,scale):
        save(f"accepted_{record['accepted_iteration']:04d}.npz",dict(coefficients=e,raw_fields=P@e,
            canonical_momentum_target=data['canonical_momentum'],frame_reactions=rho,
            original_constitutive_rows=r,framed_rows=f,framed_Jacobian=J,row_scale=scale,
            action_gradient=a['gradient'],action_hessian=a['hessian']))
        print(json.dumps(record,sort_keys=True),flush=True)
    a=safeguarded_complex_constitutive(previous_arrays['coefficients'],data['canonical_momentum'],
        evaluate,frame,starting_reactions=previous_arrays['frame_reactions'],
        max_evaluations=max_evaluations,checkpoint=checkpoint)
    save('application.npz',dict(coefficients=a['coefficients'],raw_fields=P@a['coefficients'],
        canonical_momentum_target=data['canonical_momentum'],original_constitutive_rows=a['original_constitutive_rows'],
        framed_rows=a['framed_rows'],framed_Jacobian=a['framed_Jacobian'],frame_reactions=a['frame_reactions'],
        action_gradient=a['action']['gradient'],action_hessian=a['action']['hessian'],row_scale=a['row_scale'],
        variable_scale=a['variable_scale'],literal_generators=frame['literal_generators'],
        named_frame_covectors=frame['named_frame_covectors'],coordinate_time=np.array(time),
        original_terminal_master=data['master_coefficients'],resume_master=previous_arrays['coefficients']))
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),):refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):
        raise RuntimeError('same action/source changed during resumed application')
    result=dict(classification='RESUMED_SAFEGUARDED_FULL_COMPLEX_CONSTITUTIVE_RESIDUAL',
        input_hashes=refs,archives=archives,action_parameters=parameters,status=a['status'],history=a['history'],
        original_rows_max=float(np.max(abs(a['original_constitutive_rows']))),
        original_momentum_residual_max=float(np.max(abs(a['original_constitutive_rows'][:106]))),
        original_algebraic_residual_max=float(np.max(abs(a['original_constitutive_rows'][106:]))),
        original_rows_norm=float(np.linalg.norm(a['original_constitutive_rows'])),
        velocity_algebraic_change_from_original_norm=float(np.linalg.norm(a['coefficients'][106:]-data['master_coefficients'][106:])),
        same_fixed_x_and_supplied_action_Pi=True,
        frame_reference_reset_rounding_defect_max=float(np.max(abs(frame_reference_defect))),
        numerical_merit_normalization_reinitialized_at_saved_state=True,
        invalid_chart_trials=a['invalid_chart_trials'],total_action_evaluations=a['total_action_evaluations'],
        optimizer_status=a['optimizer_status'],optimizer_message=a['optimizer_message'],max_evaluations=max_evaluations,
        original_rows_or_singular_directions_removed=False,action_regularization_used=False,
        physical_branch_stationarity_first_hit_or_Pauli_selected=False)
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=a['status'],original_rows_max=result['original_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest()),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--terminal-folder',type=Path,default=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-evaluations',type=int,default=200)
    a=p.parse_args();materialize(a.previous,a.terminal_folder,a.output,max_evaluations=a.max_evaluations)
