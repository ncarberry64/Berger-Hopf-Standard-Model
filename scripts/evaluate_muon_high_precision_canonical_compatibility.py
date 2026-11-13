"""Correct all original146 rows directly at the reached nearroot point."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from evaluate_muon_continued_current_factor import retained_input
from bhsm.interface.muon_complex_canonical_compatibility import canonical_central_frame
from bhsm.interface.muon_warm_complex_canonical_compatibility import warm_complex_constitutive_compatibility
from bhsm.interface.muon_high_precision_canonical_compatibility import high_precision_original_constitutive_action,precise_constitutive_directional_control
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def materialize(initial_folder,output,precision,max_iterations,tolerance):
    source=ROOT/initial_folder;out=ROOT/output
    if out.exists():raise FileExistsError('preserve every direct original146 precise-gradient application')
    refs={}
    def read(path):
        p=ROOT/path;b=p.read_bytes();refs[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    md=read(initial_folder/'result.json');refs.update(md['input_hashes']);data=read(initial_folder/'application.npz')
    if refs[(initial_folder/'application.npz').as_posix()]!=md['archives']['application.npz']['sha256']:
        raise ValueError('same original nearroot state changed')
    terminal=read(Path('artifacts/muon_holomorphic_child_terminal_20261011/run_2/actual_complex_terminal_full_action.npz'))
    phase,_=retained_input('outgoing',refs);P=phase['coordinates']['lift'];rep=phase['representation'];n=106
    eta=data['coefficients'];Pi=data['canonical_momentum_target'];time=data['coordinate_time'].item();params=md['action_parameters']
    reference=data['original_frame_reference'];rho=data['frame_reactions']
    if not np.array_equal(eta[:n],terminal['master_coefficients'][:n])or not np.array_equal(Pi,terminal['canonical_momentum']):
        raise ValueError('original terminal x/Pi must remain byte-identical')
    if not np.array_equal(reference,terminal['master_coefficients'][n:]):raise ValueError('original named frame reference changed')
    frame=canonical_central_frame(terminal['raw_fields'],rep)
    evaluate=lambda e:high_precision_original_constitutive_action(P@e,time,phase['arrays']['initial_pair'],
        phase['arrays']['reference_pair'],rep,decimal_precision=precision,**params)
    out.mkdir(parents=True);archives={}
    def save(name,arrays):
        p=out/name;_compressed_npz(p,arrays)
        if p.stat().st_size>10*1024**2:raise RuntimeError('split complete original action applications')
        archives[name]=dict(bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest())
    # This independent mixed nonreal direction is fixed before Newton and
    # preserves the actual original chart, target and all derivative rows.
    j=np.arange(146);direction=(np.sin(.71*(j+1))+.37j*np.cos(.43*(j+1)))/np.sqrt(146)
    control=precise_constitutive_directional_control(eta,direction,evaluate,steps=(2e-4,2e-3))
    save('precise_gradient_original_Hessian_direction_control.npz',control['arrays'])
    print(json.dumps(dict(stage='same_action_precise146_Hessian_control',records=control['records']),sort_keys=True),flush=True)
    if min(r['relative_difference_norm']for r in control['records'])>3e-6:
        raise ValueError('same-action original Hessian derivative control failed before Newton')
    def checkpoint(i,e,rho,a,r,f,K,scale,history):
        save(f'iteration_{i:04d}.npz',dict(coefficients=e,raw_fields=P@e,frame_reactions=rho,
            action_gradient=a['gradient'],binary_action_gradient=a['binary_original_gradient'],
            action_Hessian=a['hessian'],original_constitutive_rows=r,framed_rows=f,
            framed_Jacobian=K,row_scale=scale,canonical_momentum_target=Pi,
            original_frame_reference=reference,coordinate_time=np.array(time),
            high_precision_gradient_decimal_strings=a['high_precision_gradient_decimal_strings']))
        print(json.dumps(dict(stage='direct_original146_precise_gradient_Newton',**history[-1]),sort_keys=True),flush=True)
    result=warm_complex_constitutive_compatibility(eta,Pi,evaluate,frame,
        frame_reference=reference,start_reaction=rho,max_iterations=max_iterations,
        tolerance=tolerance,checkpoint=checkpoint)
    a=result['action'];r=result['original_constitutive_rows'];binary_r=a['binary_original_gradient'][n:]-np.r_[Pi,np.zeros(40,complex)]
    save('application.npz',dict(coefficients=result['coefficients'],raw_fields=P@result['coefficients'],
        original_terminal_master=terminal['master_coefficients'],original_frame_reference=reference,
        canonical_momentum_target=Pi,coordinate_time=np.array(time),action_gradient=a['gradient'],
        action_Hessian=a['hessian'],original_constitutive_rows=r,binary_original_constitutive_rows=binary_r,
        binary_action_gradient=a['binary_original_gradient'],original_force=a['gradient'][:n],
        high_precision_gradient_decimal_strings=a['high_precision_gradient_decimal_strings'],
        framed_rows=result['framed_rows'],framed_Jacobian=result['framed_Jacobian'],
        frame_reactions=result['frame_reactions'],named_frame_covectors=frame['named_frame_covectors'],
        literal_gauge_generators=frame['literal_generators'],literal_generator_image=result['literal_generator_image'],
        literal_gauge_source_compatibility=result['literal_gauge_source_compatibility'],
        fixed_position_defect=result['fixed_position_defect'],action_value=np.array(a['value'])))
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.')and path:
            try:rel=Path(path).relative_to(ROOT).as_posix()
            except ValueError:continue
            refs[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    refs[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('same original signed action sources changed')
    record=dict(classification='EVALUATED_DIRECT_ORIGINAL146_PRECISE_GRADIENT_FRAMED_CANONICAL_CORRECTION',
        input_hashes=refs,archives=archives,decimal_precision=precision,status=result['status'],history=result['history'],
        tolerance=tolerance,original_rows_max=float(np.max(abs(r))),original_momentum_rows_max=float(np.max(abs(r[:n]))),
        original_algebraic_rows_max=float(np.max(abs(r[n:]))),original84_field_rows_max=float(np.max(abs(r[np.r_[38:106,130:146]]))),
        binary_original_rows_max=float(np.max(abs(binary_r))),precise_minus_binary_gradient_max=float(np.max(abs(r-binary_r))),
        original_fixed_position_defect_max=float(np.max(abs(result['fixed_position_defect']))),
        velocity_algebraic_correction_from_resume_norm=float(np.linalg.norm(result['coefficients'][n:]-eta[n:])),
        literal_gauge_source_compatibility_max=float(np.max(abs(result['literal_gauge_source_compatibility']))),
        named_frame_reaction_max=float(np.max(abs(result['frame_reactions']))),Hessian_direction_control=control['records'],
        all_original146_rows_and_two_named_frames_retained=True,original_target_or_reference_changed=False,
        quadratic_re_elimination_performed=False,action_parameters=params,lambda_H=rep['scalar_matching']['lambda_H'],
        original_force_and_binary_Hessian_retained=True,initial_state_compatible=bool(np.max(abs(r))<=tolerance and np.max(abs(result['framed_rows']))<=tolerance),
        physical_first_hit_exterior_domain_or_Pauli_selected=False,
        error_scope='literal arbitraryprecision original finite signed-action tail gradient, binary same-action Hessian/position force with independent directional controls; fixed binary positional/source/quadrature coefficients, no outward physical or anomaly enclosure')
    p=out/'result.json';p.write_text(json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='direct_original146_precise_gradient_complete',status=result['status'],
        original_rows_max=record['original_rows_max'],binary_original_rows_max=record['binary_original_rows_max'],
        result_sha256=sha256(p.read_bytes()).hexdigest())),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--initial-folder',type=Path,default=Path('artifacts/muon_material_rate_canonical_geometry_20261011/continued_run_1'))
    p.add_argument('--output',type=Path,required=True);p.add_argument('--precision',type=int,default=60)
    p.add_argument('--max-iterations',type=int,default=8);p.add_argument('--tolerance',type=float,default=2e-10)
    a=p.parse_args();materialize(a.initial_folder,a.output,a.precision,a.max_iterations,a.tolerance)
