"""Canonical phase continuation on the evaluated trace-enriched action.

The actual paired endpoint fields and affine source-image basis are
consumed together.  Refining quadrature changes integration points, not
the frozen basis or its coefficients.  Canonical momenta are carried
between steps; all multiplier and Gauss equations are retained.  This
is a finite assigned-action continuation, not physical formation or a
replacement for complementary wall/event equations.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT,correction_representation
from .muon_birth_phase_continuation import phase_continuation,discrete_action_cotangents,_compressed_npz
from .muon_birth_trace_enriched_action import (
    trace_enriched_radial_basis,generic_coordinate_lift,
    pointwise_trace_enriched_action,trace_enriched_wall_conormal,
)
from .muon_parent_maxwell_full_weak import FIELD_ORDER


def enriched_representation_from_values(receipt,arrays,*,radial_points=None,cap_points=None):
    """Recover the recorded numerical frame, with optional quadrature refinement."""
    rp=receipt['radial_points'] if radial_points is None else radial_points
    cp=receipt['cap_points'] if cap_points is None else cap_points
    rep=correction_representation(radial_points=rp,radial_order=2,cap_points=cp,
        include_wall_lift=True,include_scalar_mean=True)
    metadata=receipt['affine_profile_enrichment']
    names=('affine_profile_reference_states','affine_interior_projection','affine_difference_coefficients',
        'wall_trace_map','wall_radial_derivative_map')
    for name in names:rep[name]=np.array(arrays[name],copy=True)
    rep.update(gauge_labels=receipt['gauge_labels'],gauge_count=receipt['gauge_count'],
        affine_wall_coefficient=metadata['wall_coefficient'],affine_complement_norm=metadata['boundary_anchored_complement_norm'],
        former_radial_space_L2_complement=metadata['former_radial_space_L2_complement'],radial_function_count=4)
    if receipt['gauge_count']!=80:raise ValueError('recorded complete five-component enriched frame required')
    if rep['wall_trace_map'].shape!=(5,4,80):raise ValueError('recorded actual wall map required')
    value,derivative=trace_enriched_radial_basis(rep,rep['rho'])
    gb=np.zeros((rp,80,1,5,4));gr=gb.copy()
    for k,label in enumerate(rep['gauge_labels']):
        field=FIELD_ORDER.index(label['field']);internal=label['internal'];radial=label['radial']
        gb[:,k,0,field,internal]=value[:,radial];gr[:,k,0,field,internal]=derivative[:,radial]
    rep.update(gauge_basis=gb,gauge_radial_basis=gr,radial_value_map=value,radial_derivative_map=derivative,
        basis_refinement_policy='recorded source profile, projection coefficients, normalization and wall map held fixed; integration points refined')
    if rp==receipt['radial_points']:
        for name in ('gauge_basis','gauge_radial_basis','radial_value_map','radial_derivative_map','rho','radial_quadrature'):
            if not np.array_equal(rep[name],arrays[name]):raise ValueError('recorded numerical frame does not reconstruct exactly: '+name)
    return rep


def load_enriched_endpoint(initial_application,*,side,repository=ROOT,radial_points=None,cap_points=None):
    root=Path(repository);source=Path(initial_application);source=source if source.is_absolute() else root/source
    if side not in ('incoming','outgoing'):raise ValueError('actual incoming or outgoing arm required')
    raw_receipt=(source/'result.json').read_bytes();receipt=json.loads(raw_receipt)
    if receipt['status']!='REPRESENTED_TEMPORAL_FIELD_TOLERANCE':raise ValueError('consume an evaluated paired endpoint correction')
    for path,digest in receipt['input_hashes'].items():
        if sha256((root/path).read_bytes()).hexdigest()!=digest:raise ValueError('consumed action owner changed: '+path)
    data=(source/'application.npz').read_bytes()
    if sha256(data).hexdigest()!=receipt['numerical_sha256']:raise ValueError('paired endpoint values changed')
    with np.load(source/'application.npz',allow_pickle=False) as saved:arrays={k:saved[k] for k in saved.files}
    rep=enriched_representation_from_values(receipt,arrays,radial_points=radial_points,cap_points=cap_points)
    raw=arrays['updated_raw_pair'][0 if side=='incoming' else 1].copy()
    coordinates=generic_coordinate_lift(rep['gauge_labels']);P=coordinates['lift'];eta=P.T@raw
    if not np.array_equal(P@eta,raw):raise ValueError('canonical lift must preserve all endpoint fields; no At-rate coordinate silently discarded')
    return dict(raw=raw,master=eta,representation=rep,coordinates=coordinates,
        receipt=receipt,receipt_sha256=sha256(raw_receipt).hexdigest(),source=source)


def materialize_trace_enriched_phase(initial_application,output,*,side,span,steps,
        radial_points=None,cap_points=None,max_iterations=10,repository=ROOT,resume_checkpoint=None):
    root=Path(repository);out=Path(output)
    if out.exists():raise FileExistsError('preserve earlier numerical evidence')
    if (side=='incoming' and span>=0) or (side=='outgoing' and span<=0):
        raise ValueError('incoming past / outgoing future from common birth0 required')
    input=load_enriched_endpoint(initial_application,side=side,repository=root,radial_points=radial_points,cap_points=cap_points)
    rep=input['representation'];P=input['coordinates']['lift'];nx=input['coordinates']['x_count'];eta0=input['master']
    params=input['receipt']['action_parameters'];evaluate=lambda eta:pointwise_trace_enriched_action(P@eta,rep,**params)
    hashes=dict(input['receipt']['input_hashes'])
    path='src/bhsm/interface/muon_birth_trace_enriched_phase.py';hashes[path]=sha256((root/path).read_bytes()).hexdigest()
    a0=evaluate(eta0);p0=a0['gradient'][nx:2*nx]
    x_start=eta0[:nx];p_start=p0;guess_start=eta0;start_stage=0;resume_sha=None;resume_options={}
    if resume_checkpoint is not None:
        cp=Path(resume_checkpoint);cp=cp if cp.is_absolute() else root/cp;cb=(cp/'result.json').read_bytes();cr=json.loads(cb)
        if cr['input_hashes']!=hashes or cr['consumed_receipt_sha256']!=input['receipt_sha256']:
            raise ValueError('resume must preserve pinned paired endpoint and action')
        if (cr['side'],cr['span'],cr['steps'],cr['radial_points'],cr['cap_points'])!=(side,span,steps,len(rep['rho']),rep['cap_points']):
            raise ValueError('resume must preserve orientation, span, frozen basis and quadrature')
        if sha256((cp/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:raise ValueError('checkpoint changed')
        with np.load(cp/'application.npz',allow_pickle=False) as saved:
            x_start=saved['incoming_x'];p_start=saved['incoming_p'];guess_start=saved['stage_guess']
            resume_options=dict(resumed_unknowns=saved['unknowns'],resumed_row_scale=saved['row_scale'],resumed_iteration=cr['iteration'])
        start_stage=cr['stage'];resume_sha=sha256(cb).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(stage,iteration,z,a,scale,history,status,x,p,eta):
        folder=out/'checkpoints'/f'stage_{stage:04d}'/f'accepted_{iteration:04d}';folder.mkdir(parents=True)
        _compressed_npz(folder/'application.npz',dict(incoming_x=x,incoming_p=p,stage_guess=eta,
            unknowns=z,residual=a['residual'],jacobian=a['jacobian'],row_scale=scale,midpoint_raw=P@a['midpoint_coefficients']))
        md=dict(scope='TRACE_ENRICHED_ACTION_PHASE_CHECKPOINT',stage=stage,iteration=iteration,status=status,
            side=side,span=span,steps=steps,radial_points=len(rep['rho']),cap_points=rep['cap_points'],action_parameters=params,
            scaled_residual=float(np.linalg.norm(scale*a['residual'])),iteration_history=history,
            input_hashes=hashes,consumed_receipt_sha256=input['receipt_sha256'],
            numerical_sha256=sha256((folder/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_trace_enriched_phase',
                '--initial-application',str(input['source']),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY',
                '--side',side,'--span',str(span),'--steps',str(steps),'--radial-points',str(len(rep['rho'])),
                '--cap-points',str(rep['cap_points']),'--max-iterations',str(max_iterations),'--resume-checkpoint',str(folder)],
            resume_environment=dict(PYTHONPATH='src'))
        (folder/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    result=phase_continuation(x_start,p_start,guess_start,span,steps,evaluate,max_iterations=max_iterations,
        checkpoint=checkpoint,start_stage=start_stage,**resume_options)
    if hashes!={p:sha256((root/p).read_bytes()).hexdigest() for p in hashes}:raise RuntimeError('owner changed during continuation')
    stages=result['applications'];apps=[s['application'] for s in stages];contacts=[discrete_action_cotangents(a,result['step']) for a in apps]
    conormals=[trace_enriched_wall_conormal(P@a['midpoint_coefficients'],rep)['radial_action_covector'] for a in apps]
    arrays=dict(initial_raw=input['raw'],initial_master=eta0,initial_p=p0,x_final=result['x_final'],p_final=result['p_final'],
        stage_indices=np.array([s['stage'] for s in stages]),stage_unknowns=np.array([s['unknowns'] for s in stages]),
        stage_midpoint_raw=np.array([P@a['midpoint_coefficients'] for a in apps]),stage_residual=np.array([a['residual'] for a in apps]),
        stage_row_scale=np.array([s['row_scale'] for s in stages]),stage_jacobian=np.array([a['jacobian'] for a in apps]),
        stage_initial_face=np.array([c['initial_face'] for c in contacts]),stage_final_face=np.array([c['final_face'] for c in contacts]),
        material_wall_conormals=np.array(conormals),wall_trace_map=rep['wall_trace_map'],wall_radial_derivative_map=rep['wall_radial_derivative_map'],
        radial_value_map=rep['radial_value_map'],radial_derivative_map=rep['radial_derivative_map'],rho=rep['rho'],radial_quadrature=rep['radial_quadrature'])
    for s in stages:
        if s['records']:
            for name in s['records'][0]:arrays[f'stage_{s["stage"]:04d}_iteration_{name}']=np.array([r[name] for r in s['records']])
    _compressed_npz(out/'application.npz',arrays)
    md=dict(scope='EVALUATED_TRACE_ENRICHED_ASSIGNED_ACTION_PHASE_CONTINUATION',side=side,span=span,steps=steps,
        completed_steps=result['completed_steps'],resumed_stage=start_stage,resumed_checkpoint_sha256=resume_sha,
        raw_count=len(input['raw']),gauge_count=rep['gauge_count'],gauge_labels=rep['gauge_labels'],
        dynamic_count=nx,algebraic_count=input['coordinates']['y_count'],actual_canonical_momentum_carried=True,
        stages=[dict(status=s['status'],scaled_residual=s['scaled_residual'],history=s['history']) for s in stages],
        finite_euler_norms=[float(np.linalg.norm(a['finite_dynamic_euler'])) for a in apps],
        constraint_norms=[float(np.linalg.norm(a['algebraic_constraint'])) for a in apps],
        canonical_initial_contact_defects=[float(np.linalg.norm(c['initial_face']+s['incoming_p'])) for c,s in zip(contacts,stages)],
        canonical_final_contact_defects=[float(np.linalg.norm(c['final_face']-a['p_new'])) for c,a in zip(contacts,apps)],
        wall_conormal_norms=[float(np.linalg.norm(c)) for c in conormals],
        action_parameters=params,radial_points=len(rep['rho']),cap_points=rep['cap_points'],input_hashes=hashes,
        consumed_receipt_sha256=input['receipt_sha256'],consumed_coefficients_sha256=input['receipt']['numerical_sha256'],
        consumed_paired_endpoint_path=input['source'].relative_to(root).as_posix(),
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        all_multiplier_and_Gauss_rows_retained=True,numerical_rank_not_physical_gauge_count=True,regularizing_shift=0.,
        quadrature_policy=rep['basis_refinement_policy'],
        temporal_scope='incoming23 past / outgoing24 future from common E1, finite numerical span; no physical E0 or finalchild endpoint imposed',
        lateral_scope='radial wall covectors exported separately, not replaced by temporal matching or zero conditions',
        physical_scale_equation='GF=cF[common charged-current action]/E_kappa^2',
        unassigned_area_equation='gamma=alpha_FSC*ell_current^(-m), no alpha_EM substitution or gamma0 claim',
        physical_birth_formation_closed=False,physical_native_heat_closed=False,physical_Pauli_value=False,
        error_scope='binary64 finite action and analytic Newton Jacobian; no continuum or producer-rounding certificate; exact energy conservation not asserted')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--initial-application',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--side',choices=('incoming','outgoing'),required=True);p.add_argument('--span',type=float,required=True);p.add_argument('--steps',type=int,required=True)
    p.add_argument('--radial-points',type=int);p.add_argument('--cap-points',type=int);p.add_argument('--max-iterations',type=int,default=10)
    p.add_argument('--resume-checkpoint',type=Path);a=p.parse_args()
    print(json.dumps(materialize_trace_enriched_phase(a.initial_application,a.output,side=a.side,span=a.span,steps=a.steps,
        radial_points=a.radial_points,cap_points=a.cap_points,max_iterations=a.max_iterations,resume_checkpoint=a.resume_checkpoint),sort_keys=True))
