"""Apply actual complex terminal constitutive rows without changing x or Pi."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_holomorphic_child_action import holomorphic_inherited_child_action
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame,complex_constitutive_compatibility
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(terminal_folder,output,*,max_iterations):
    base=ROOT/terminal_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every constitutive application')
    rb=(base/'result.json').read_bytes();md=json.loads(rb);refs=dict(md['input_hashes'])
    refs[(base/'result.json').relative_to(ROOT).as_posix()]=sha256(rb).hexdigest()
    path=base/'actual_complex_terminal_full_action.npz';h=sha256(path.read_bytes()).hexdigest()
    if h!=md['archives'][path.name]['sha256']:raise ValueError('same actual complex terminal changed')
    refs[path.relative_to(ROOT).as_posix()]=h
    with np.load(path,allow_pickle=False)as z:data={k:z[k].copy()for k in z.files}
    phase,_=retained_input('outgoing',refs);rep=phase['representation'];P=data['coordinate_lift'];time=data['coordinate_time'].item()
    if not np.array_equal(P,phase['coordinates']['lift']):raise ValueError('all original252 same-coordinate rows required')
    evaluate=lambda e:holomorphic_inherited_child_action(P@e,time,phase['arrays']['initial_pair'],phase['arrays']['reference_pair'],rep,**md['action_parameters'])
    frame=canonical_central_frame(data['raw_fields'],rep);out.mkdir(parents=True);archives={}
    def save(name,a):
        p=out/name;_compressed_npz(p,a)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete original rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def checkpoint(i,e,rho,a,r,f,K,hist):
        save(f'iteration_{i}_full_constitutive_action.npz',dict(coefficients=e,raw_fields=P@e,
            canonical_momentum_target=data['canonical_momentum'],action_gradient=a['gradient'],action_hessian=a['hessian'],
            original_constitutive_rows=r,framed_rows=f,framed_Jacobian=K,frame_reactions=rho,
            literal_generators=frame['literal_generators'],named_frame_covectors=frame['named_frame_covectors']))
        print(json.dumps(dict(stage='same_complex_terminal_constitutive',**hist[-1]),sort_keys=True),flush=True)
    a=complex_constitutive_compatibility(data['master_coefficients'],data['canonical_momentum'],evaluate,frame,
        max_iterations=max_iterations,checkpoint=checkpoint)
    save('application.npz',dict(coefficients=a['coefficients'],raw_fields=P@a['coefficients'],coordinate_time=np.array(time),
        canonical_momentum_target=a['canonical_momentum_target'],canonical_force=a['action']['gradient'][:106],
        original_constitutive_rows=a['original_constitutive_rows'],framed_rows=a['framed_rows'],
        literal_generator_image=a['literal_generator_image'],literal_gauge_source_compatibility=a['literal_gauge_source_compatibility'],
        frame_reactions=a['frame_reactions'],position_defect=a['fixed_position_defect'],original_terminal_master=data['master_coefficients']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    for rel in(Path(__file__).relative_to(ROOT).as_posix(),'tests/test_muon_complex_canonical_compatibility.py'):
        refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    if any(sha256((ROOT/r).read_bytes()).hexdigest()!=h for r,h in refs.items()):raise RuntimeError('same canonical action/source changed')
    result=dict(classification='EVALUATED_SAME_COMPLEX_TERMINAL_CANONICAL_CONSTITUTIVE_COMPATIBILITY',input_hashes=refs,archives=archives,
        status=a['status'],history=a['history'],max_iterations=max_iterations,
        position_change_max=float(np.max(abs(a['fixed_position_defect']))),
        original_Lv_minus_supplied_Pi_max=float(np.max(abs(a['original_constitutive_rows'][:106]))),
        original_Gauss_multiplier_max=float(np.max(abs(a['original_constitutive_rows'][106:]))),
        original_Gauss_multiplier_norm=float(np.linalg.norm(a['original_constitutive_rows'][106:])),
        original_rows_max=float(np.max(abs(a['original_constitutive_rows']))),
        literal_gauge_compatibility_max=float(np.max(abs(a['literal_gauge_source_compatibility']))),
        named_frame_reaction_max=float(np.max(abs(a['frame_reactions']))),
        velocity_algebraic_change_norm=float(np.linalg.norm(a['coefficients'][106:]-data['master_coefficients'][106:])),
        all_original146_rows_retained=True,central_gauge_generator_includes_Hdot=True,
        same_original_terminal_x_and_Pi_target=True,old_real_phase_p_used_as_target=False,
        numerical_eigenvectors_or_pseudoinverse_used=False,physical_gauge_quotient_selected=False,
        canonical_time_step_or_first_hit_selected=False,
        next_equation='with compatible initial data, D_t Pi=L_x and xdot=v; stop only at first descending selected same-action eigenvalue lambda_selected=0',
        error_scope='binary64 full analytic constrained constitutive solve and named frame reaction; no continuum/domain/physical first-hit or Pauli error enclosure')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='same_complex_constitutive_complete',status=result['status'],
        original_rows_max=result['original_rows_max'],Gauss_multiplier_max=result['original_Gauss_multiplier_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--terminal-folder',type=Path,default=Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--max-iterations',type=int,default=3)
    a=p.parse_args();materialize(a.terminal_folder,a.output,max_iterations=a.max_iterations)
