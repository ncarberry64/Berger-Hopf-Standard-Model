"""Apply all148 safeguarded constitutive rows on the actual complex terminal."""
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


def materialize(terminal_folder,output,*,max_evaluations=80):
    folder=ROOT/terminal_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve each actual canonical residual probe')
    md=json.loads((folder/'result.json').read_bytes());refs=dict(md['input_hashes'])
    for p in ('result.json','actual_complex_terminal_full_action.npz'):
        f=folder/p;refs[f.relative_to(ROOT).as_posix()]=sha256(f.read_bytes()).hexdigest()
    with np.load(folder/'actual_complex_terminal_full_action.npz',allow_pickle=False)as z:
        data={k:z[k].copy()for k in z.files}
    if refs[(folder/'actual_complex_terminal_full_action.npz').relative_to(ROOT).as_posix()]!=md['archives']['actual_complex_terminal_full_action.npz']['sha256']:
        raise ValueError('same full complex terminal action required')
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=data['coordinate_lift']
    time=data['coordinate_time'].item();params=md['action_parameters']
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time,
        phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**params)
    frame=canonical_central_frame(data['raw_fields'],rep);out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete action rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def checkpoint(record,e,rho,a,r,f,J,scale):
        save(f"accepted_{record['accepted_iteration']:04d}.npz",dict(coefficients=e,raw_fields=P@e,
            canonical_momentum_target=data['canonical_momentum'],frame_reactions=rho,
            original_constitutive_rows=r,framed_rows=f,framed_Jacobian=J,row_scale=scale,
            action_gradient=a['gradient'],action_hessian=a['hessian']))
        print(json.dumps(record,sort_keys=True),flush=True)
    a=safeguarded_complex_constitutive(data['master_coefficients'],data['canonical_momentum'],evaluate,frame,
        max_evaluations=max_evaluations,checkpoint=checkpoint)
    save('application.npz',dict(coefficients=a['coefficients'],raw_fields=P@a['coefficients'],
        canonical_momentum_target=data['canonical_momentum'],original_constitutive_rows=a['original_constitutive_rows'],
        framed_rows=a['framed_rows'],framed_Jacobian=a['framed_Jacobian'],frame_reactions=a['frame_reactions'],
        action_gradient=a['action']['gradient'],action_hessian=a['action']['hessian'],row_scale=a['row_scale'],
        variable_scale=a['variable_scale'],literal_generators=frame['literal_generators'],
        named_frame_covectors=frame['named_frame_covectors'],coordinate_time=np.array(time),
        original_terminal_master=data['master_coefficients']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_safeguarded_complex_constitutive.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):
        raise RuntimeError('same canonical action/source changed during probe')
    result=dict(classification='EVALUATED_SAFEGUARDED_FULL_COMPLEX_CONSTITUTIVE_RESIDUAL',
        input_hashes=refs,archives=archives,status=a['status'],history=a['history'],
        original_rows_max=float(np.max(abs(a['original_constitutive_rows']))),
        original_momentum_residual_max=float(np.max(abs(a['original_constitutive_rows'][:106]))),
        original_algebraic_residual_max=float(np.max(abs(a['original_constitutive_rows'][106:]))),
        original_rows_norm=float(np.linalg.norm(a['original_constitutive_rows'])),
        original_fixed_position_max=float(np.max(abs(a['fixed_position_defect']))),
        named_frame_reaction_max=float(np.max(abs(a['frame_reactions']))),
        literal_gauge_source_max=float(np.max(abs(a['literal_gauge_source']))),
        invalid_chart_trials=a['invalid_chart_trials'],total_action_evaluations=a['total_action_evaluations'],
        optimizer_status=a['optimizer_status'],optimizer_message=a['optimizer_message'],max_evaluations=max_evaluations,
        numerical_trust_region_not_action_regularization=True,original_rows_or_singular_directions_removed=False,
        action_parameters=params,same_fixed_x_and_supplied_action_Pi=True,
        physical_branch_stationarity_first_hit_or_Pauli_selected=False)
    p=out/'result.json';p.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=a['status'],original_rows_max=result['original_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest()),sort_keys=True),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--terminal-folder',type=Path,default=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-evaluations',type=int,default=80)
    a=p.parse_args();materialize(a.terminal_folder,a.output,max_evaluations=a.max_evaluations)
