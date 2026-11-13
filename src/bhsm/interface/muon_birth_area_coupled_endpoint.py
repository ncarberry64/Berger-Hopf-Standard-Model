"""Positive-area continuation of the actual full-field birth action rows.

The area source response is a Newton initializer, not a branch choice.
Every geometric/field trace, dual, constraint, energy and normal row is
re-evaluated at the corrected common vector.  The supplied gamma is a
family continuation parameter; no physical c or formation mode is selected.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT,STATE_SOURCE
from .muon_birth_reset_evaluation import NORMALIZATION_SOURCE
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_finite_geometric_trace_endpoint import solve_moving_endpoint
from .muon_birth_phase_continuation import _compressed_npz


def area_continuation_initializer(raw_pair, parameter_response, gamma):
    """The same-vector first parameter step, with no physical interpretation."""
    raw=np.asarray(raw_pair);delta=np.asarray(parameter_response)
    if (not np.isrealobj(raw)or not np.isrealobj(delta)or raw.shape!=delta.shape
            or raw.ndim!=2 or raw.shape[0]!=2 or not np.isfinite(raw).all()
            or not np.isfinite(delta).all()or not np.isfinite(gamma)or gamma<=0):
        raise ValueError('complete real pair, its area parameter derivative and positive gamma required')
    return raw+float(gamma)*delta


def materialize_area_coupled_endpoint(base_directory,area_response_directory,output,*,
        gamma,max_iterations=6,difference_step=2e-5,repository=ROOT,resume_checkpoint=None):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier coupled parameter corrections')
    base=load_finite_normal_endpoint(base_directory,side='incoming',repository=root)
    rep=base['representation'];params=dict(base['receipt']['action_parameters']);params['surface_gamma']=float(gamma)
    if not np.isfinite(gamma)or gamma<=0:raise ValueError('positive area family continuation parameter required')
    rep['endpoint_action_parameters']=params
    with np.load(base['source']/'application.npz',allow_pickle=False)as f:saved={k:f[k].copy()for k in f.files}
    path=Path(area_response_directory);path=path if path.is_absolute()else root/path
    arb=(path/'result.json').read_bytes();ar=json.loads(arb)
    for p,h in ar['input_hashes'].items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('area response owner changed: '+p)
    az=(path/'application.npz').read_bytes()
    if sha256(az).hexdigest()!=ar['numerical_sha256']:raise ValueError('area initializer arrays changed')
    with np.load(path/'application.npz',allow_pickle=False)as f:delta=f['raw_parameter_response'].copy()
    initial=area_continuation_initializer(saved['updated_raw_pair'],delta,gamma)
    reference=saved['reference_raw_pair'];refs=dict(base['input_hashes'])
    refs[(path/'result.json').relative_to(root).as_posix()]=sha256(arb).hexdigest()
    refs[(path/'application.npz').relative_to(root).as_posix()]=sha256(az).hexdigest()
    for name in ('muon_birth_area_coupled_endpoint','muon_birth_finite_geometric_trace_endpoint',
                 'muon_birth_finite_normal_trace_graph','muon_exact_material_response'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    with np.load(root/STATE_SOURCE,allow_pickle=False)as f:weights=f['state_weights'].copy()
    with np.load(root/NORMALIZATION_SOURCE,allow_pickle=False)as f:normal=f['normalization_coordinates'].copy()
    resumed={};resume_hash=None
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute()else root/cp;cb=(cp/'result.json').read_bytes();cr=json.loads(cb)
        if cr['input_hashes']!=refs or cr['gamma']!=float(gamma)or cr['difference_step']!=difference_step:
            raise ValueError('resume must preserve full action, area parameter and numerical differentiation')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint values changed')
        with np.load(cp/'application.npz',allow_pickle=False)as f:
            initial=f['raw_pair'].copy();resumed=dict(row_scale=f['row_scale'].copy(),iteration_offset=cr['accepted_iteration'])
        resume_hash=sha256(cb).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(k,raw,current,scale,history):
        folder=out/'checkpoints'/f'accepted_{k:04d}';folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz',dict(raw_pair=raw,residual=current['residual'],
            jacobian=current['jacobian'],row_scale=scale,common_trace_cotangent=current['projected']['cotangent']))
        md=dict(classification='AREA_COUPLED_ACCEPTED_ENDPOINT_CHECKPOINT',accepted_iteration=k,
            gamma=float(gamma),difference_step=difference_step,input_hashes=refs,history=history,
            numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_area_coupled_endpoint',
                '--base-directory',str(base['source']),'--area-response-directory',str(path),
                '--output','CHOOSE_NEW_OUTPUT_DIRECTORY','--gamma',str(gamma),'--max-iterations',str(max_iterations),
                '--difference-step',str(difference_step),'--resume-checkpoint',str(folder)],
            resume_environment=dict(PYTHONPATH='src'))
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    solved=solve_moving_endpoint(initial,reference,rep,weights,normal,max_iterations=max_iterations,
        difference_step=difference_step,checkpoint=checkpoint,**resumed)
    if refs!={p:sha256((root/p).read_bytes()).hexdigest()for p in refs}:raise RuntimeError('owned action changed during correction')
    a=solved['application'];p=a['projected'];arrays={}
    for key in ('affine_profile_reference_states','affine_interior_projection','affine_difference_coefficients',
        'wall_trace_map','wall_radial_derivative_map','rho','radial_quadrature','gauge_basis',
        'gauge_radial_basis','radial_value_map','radial_derivative_map'):
        arrays[key]=rep[key]
    arrays.update(initial_raw_pair=initial,reference_raw_pair=reference,updated_raw_pair=solved['raw'],
        updated_residual=a['residual'],updated_jacobian=a['jacobian'],row_scale=solved['row_scale'],
        coordinate_weights=solved['coordinate_weights'],graph_raw_gradient=a['graph']['raw_gradient'],
        graph_raw_hessian=a['graph']['raw_hessian'],temporal_face_cotangent=p['face']['value'],
        temporal_face_cotangent_derivative=p['face']['first'],common_trace_cotangent=p['cotangent'],
        six_trace_cotangent=p['six_trace_cotangent'],constrained_trace_lift=p['base']['velocity_lift'],
        saddle=p['base']['saddle'],saddle_solution=p['base']['solution'],saddle_residual=p['base']['solve_residual'],
        area_parameter_initializer=delta,reference_clock_work=np.array(a['reference_clock_work']['value']))
    _compressed_npz(out/'application.npz',arrays)
    md={key:base['receipt'][key]for key in ('affine_profile_enrichment','gauge_labels','gauge_count','radial_points','cap_points')}
    md.update(classification='EVALUATED_POSITIVE_AREA_FULL_FIELD_ENDPOINT_CONTINUATION',status=solved['status'],
        action_parameters=params,gamma=float(gamma),difference_step=difference_step,resumed_checkpoint_sha256=resume_hash,
        row_count=len(a['residual']),master_unknown_count=a['jacobian'].shape[1],raw_arm_count=solved['raw'].shape[1],
        groups={name:dict(indices=list(range(*span)),norm=float(np.linalg.norm(a['residual'][slice(*span)])))for name,span in a['groups'].items()},
        scaled_residual=solved['scaled_residual'],unscaled_residual_norm=float(np.linalg.norm(a['residual'])),
        history=solved['history'],source_profile_projected=False,input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        initializer_role='same-action area parameter derivative, followed by complete nonlinear row correction',
        canonical_pullback=base['receipt']['canonical_pullback'],energy_pullback=base['receipt']['energy_pullback'],
        gamma_law='gamma=alpha_FSC*c^(-7/2); positive values here are parameter-continuation trials, not selected physical c',
        full_formation_or_physical_cutoff_or_Pauli_selected=False,
        error_scope='binary64 full represented action Newton and centered D3 adjoint derivatives; no physical branch or rigorous producer/domain enclosure')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('base-directory','area-response-directory','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--gamma',type=float,required=True);parser.add_argument('--max-iterations',type=int,default=6)
    parser.add_argument('--difference-step',type=float,default=2e-5);parser.add_argument('--resume-checkpoint',type=Path)
    args=parser.parse_args()
    print(json.dumps(materialize_area_coupled_endpoint(args.base_directory,args.area_response_directory,args.output,
        gamma=args.gamma,max_iterations=args.max_iterations,difference_step=args.difference_step,
        resume_checkpoint=args.resume_checkpoint),sort_keys=True))
