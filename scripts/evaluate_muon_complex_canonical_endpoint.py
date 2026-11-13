"""Reconstruct original endpoint v/y at an evaluated canonical x/Pi pair."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_high_precision_canonical_compatibility import high_precision_original_constitutive_action
from bhsm.interface.muon_warm_complex_canonical_compatibility import warm_complex_constitutive_compatibility
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(step_folder,output,precision,max_iterations,tolerance):
    source=ROOT/step_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every reached canonical endpoint reconstruction')
    refs={}
    def read(path):
        p=ROOT/path;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(step_folder/'result.json');refs.update(md['input_hashes']);data=read(step_folder/'application.npz')
    if refs[(step_folder/'application.npz').as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('same reached original canonical step changed')
    if md['status']!='ALL_ORIGINAL_COMPLEX_CANONICAL_ROWS_TOLERANCE' or md['all_original_stage_rows_max']>tolerance:
        raise ValueError('a compatible full original canonical step is required before endpoint reconstruction')
    initial_candidates=[Path(p).parent for p in refs if p.endswith('/application.npz') and 'high_precision_canonical_compatibility' in p]
    if len(initial_candidates)!=1:raise ValueError('the exact compatible launch and its original named reference must be identified')
    initial=read(initial_candidates[0]/'application.npz')
    phase,_=retained_input('outgoing',refs);P=phase['coordinates']['lift'];rep=phase['representation'];n=106
    eta=data['endpoint_stage_guess'].copy();Pi=data['p_final'].copy();time=data['coordinate_time_final'].item()
    reference=initial['original_frame_reference'];params=phase['receipt']['action_parameters'];rho=data['frame_reactions']
    if not np.array_equal(eta[:n],data['x_final']):raise ValueError('actual endpoint position is required')
    frame=canonical_central_frame(P@eta,rep)
    evaluate=lambda e:high_precision_original_constitutive_action(P@e,time,phase['arrays']['initial_pair'],
        phase['arrays']['reference_pair'],rep,decimal_precision=precision,**params)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete original endpoint action rows')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    def checkpoint(i,e,rho,a,r,f,K,scale,history):
        save(f'iteration_{i:04d}.npz',dict(coefficients=e,raw_fields=P@e,canonical_momentum_target=Pi,
            coordinate_time=np.array(time),action_gradient=a['gradient'],binary_action_gradient=a['binary_original_gradient'],
            action_Hessian=a['hessian'],original_constitutive_rows=r,frame_reactions=rho,
            framed_rows=f,framed_Jacobian=K,row_scale=scale,original_frame_reference=reference))
        print(json.dumps(dict(stage='original_canonical_endpoint_constitutive_reconstruction',**history[-1]),sort_keys=True),flush=True)
    result=warm_complex_constitutive_compatibility(eta,Pi,evaluate,frame,
        frame_reference=reference,start_reaction=rho,max_iterations=max_iterations,tolerance=tolerance,checkpoint=checkpoint)
    a=result['action'];r=result['original_constitutive_rows'];binary_r=a['binary_original_gradient'][n:]-np.r_[Pi,np.zeros(40,complex)]
    save('application.npz',dict(coefficients=result['coefficients'],raw_fields=P@result['coefficients'],
        canonical_momentum_target=Pi,coordinate_time=np.array(time),original_frame_reference=reference,
        original_terminal_master=initial['original_terminal_master'],endpoint_held_stage_guess=eta,
        stage_original_rows=data['original_rows'],stage_x_final=data['x_final'],stage_p_final=data['p_final'],
        stage_initial_action_cotangent=data['initial_action_cotangent'],stage_final_action_cotangent=data['final_action_cotangent'],
        action_gradient=a['gradient'],binary_action_gradient=a['binary_original_gradient'],action_Hessian=a['hessian'],
        high_precision_gradient_decimal_strings=a['high_precision_gradient_decimal_strings'],original_force=a['gradient'][:n],
        original_constitutive_rows=r,binary_original_constitutive_rows=binary_r,frame_reactions=result['frame_reactions'],
        framed_rows=result['framed_rows'],framed_Jacobian=result['framed_Jacobian'],
        named_frame_covectors=frame['named_frame_covectors'],literal_gauge_generators=frame['literal_generators'],
        literal_generator_image=result['literal_generator_image'],literal_gauge_source_compatibility=result['literal_gauge_source_compatibility']))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same original endpoint action sources changed')
    record=dict(classification='EVALUATED_ORIGINAL_COMPLEX_CANONICAL_ENDPOINT_CONSTITUTIVE_RECONSTRUCTION',input_hashes=refs,
        archives=archives,status=result['status'],history=result['history'],decimal_precision=precision,tolerance=tolerance,
        original_rows_max=float(np.max(abs(r))),original_momentum_rows_max=float(np.max(abs(r[:n]))),
        original_algebraic_rows_max=float(np.max(abs(r[n:]))),binary_original_rows_max=float(np.max(abs(binary_r))),
        precise_minus_binary_gradient_max=float(np.max(abs(r-binary_r))),
        velocity_algebraic_change_from_midpoint_guess_norm=float(np.linalg.norm(result['coefficients'][n:]-eta[n:])),
        endpoint_position_or_canonical_momentum_changed=False,original_named_frame_reference_changed=False,
        old_real_momentum_grafted=False,endpoint_midpoint_guess_used_as_constitutive_solution=False,
        all_original146_rows_Gauss_multiplier_and_two_named_frames_retained=True,
        original_force_and_binary_Hessian_retained=True,exact_endpoint_coordinate_clock_retained=True,
        action_parameters=params,lambda_H=rep['scalar_matching']['lambda_H'],
        compatible_endpoint=bool(np.max(abs(r))<=tolerance and np.max(abs(result['framed_rows']))<=tolerance),
        physical_first_hit_or_exterior_domain_selected=False,
        error_scope='same reached original canonical endpoint, literal arbitraryprecision v/y gradient and checked binary action Hessian/position force; no temporal truncation, physical stop or Pauli enclosure')
    p=out/'result.json';p.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='original_endpoint_reconstruction_complete',status=result['status'],
        original_rows_max=record['original_rows_max'],binary_original_rows_max=record['binary_original_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--step-folder',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision',type=int,default=60)
    p.add_argument('--max-iterations',type=int,default=8);p.add_argument('--tolerance',type=float,default=2e-10)
    a=p.parse_args();materialize(a.step_folder,a.output,a.precision,a.max_iterations,a.tolerance)
