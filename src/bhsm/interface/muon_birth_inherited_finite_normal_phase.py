"""Canonical child continuation retaining the corrected birth graph image.

The inherited affine connection image is unprojected.  The parent and
anchored reference germs are explicit numerical coordinate lifts; they
are not a supplied physical E0 history.  The child x/v/y coefficients are
solved with all Gauss and multiplier rows of the pulled-back action.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_finite_normal_trace_graph import (
    finite_normal_trace_graph_action_two_jet,
    affine_connection_profile_two_jet,
    pointwise_finite_normal_action,
)
from .muon_birth_phase_continuation import solve_phase_midpoint, discrete_action_cotangents, _compressed_npz
from .muon_parent_maxwell_full_weak import M
from .muon_parent_retarded_hypercharge import WALL


def affine_geometry_germ(raw, coordinate_time):
    """An explicit chart lift of the owned position/velocity first germ.

    Only geometry positions and normal amplitude advance.  The initial
    velocities and algebraic coefficients are held in this numerical lift;
    they are not asserted to solve the parent Euler equations at later time.
    The connection owner then computes consistent value/time/radial jets.
    """
    x=np.asarray(raw,float)
    if x.ndim!=1 or len(x)<100 or not np.isfinite(x).all() or not np.isfinite(coordinate_time):
        raise ValueError('complete finite first germ and coordinate time required')
    out=x.copy();out[:37]+=coordinate_time*x[37:74];out[98]+=coordinate_time*x[99]
    return out


def child_action_block(graph, parent_action, representation):
    """Restrict the literal graph two-jet to child variables at fixed parent.

    This is a restriction of the exact pulled action, rather than deletion
    of its profile image.  Parent action value is subtracted only because
    it is independent of every child variable in this application.
    """
    from .muon_birth_trace_enriched_action import generic_coordinate_lift
    c=generic_coordinate_lift(representation['gauge_labels']);P=c['lift'];nr=len(P);n=c['x_count']
    G=np.asarray(graph['raw_gradient'])[nr:];K=np.asarray(graph['raw_hessian'])[nr:,nr:]
    if G.shape!=(nr,) or K.shape!=(nr,nr):raise ValueError('complete two-arm graph required')
    g=P.T@G;k=P.T@K@P
    return dict(value=float(graph['value']-parent_action['value']),raw_gradient=G,raw_hessian=K,
        gradient=g,hessian=k,coordinates=c,Lxx=k[:n,:n],Lxv=k[:n,n:2*n],Lxy=k[:n,2*n:],
        Lvx=k[n:2*n,:n],Lvv=k[n:2*n,n:2*n],Lvy=k[n:2*n,2*n:],
        Lyx=k[2*n:,:n],Lyv=k[2*n:,n:2*n],Lyy=k[2*n:,2*n:],
        inherited_profile_increment=graph['profile_increment'],
        source_image_projected=False,parent_coordinates_held_fixed=True,
        full_stationary_birth_or_native_Pauli_established=False)


def inherited_child_finite_normal_action(raw_child, coordinate_time, initial_pair,
        reference_pair, representation, *, nu_squared_action, surface_gamma=None):
    """Apply the same child action including the exact inherited profile.

    The affine parent/reference germs are a declared computational chart,
    not new independent forcing data.  All child profile first/second
    geometry, field and wall contacts come from the existing graph owner.
    """
    child=np.asarray(raw_child,float);initial=np.asarray(initial_pair,float);reference=np.asarray(reference_pair,float)
    if initial.shape!=(2,len(child)) or reference.shape!=initial.shape:
        raise ValueError('same corrected pair and anchored reference required')
    parent=affine_geometry_germ(initial[0],coordinate_time)
    ref=np.array([affine_geometry_germ(x,coordinate_time) for x in reference])
    raw=np.array([parent,child]);params=dict(nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)
    graph=finite_normal_trace_graph_action_two_jet(raw,ref,representation,**params)
    parent_action=pointwise_finite_normal_action(parent,representation,**params)
    action=child_action_block(graph,parent_action,representation)
    # Scalar and photon consumers must retain this wall image as well.
    wall=affine_connection_profile_two_jet(raw,np.array([WALL]))
    wall_ref=affine_connection_profile_two_jet(ref,np.array([WALL]))
    dw=wall['value'][0]-wall_ref['value'][0]
    N=representation['gauge_count'];a=child[100:100+N];at=child[100+N:100+2*N]
    wall_value=np.einsum('fcj,j->fc',representation['wall_trace_map'],a)
    wall_rate=np.einsum('fcj,j->fc',representation['wall_trace_map'],at)
    wall_value[2:]+=M*dw[0];wall_rate[2:]+=M*dw[1]
    action.update(inherited_wall_profile=dw,wall_gauge=wall_value,wall_gauge_rate=wall_rate,
        coordinate_time=float(coordinate_time),parent_affine_germ=parent,reference_affine_pair=ref,
        action_clock_role='affine first-germ computational chart; not E0 or a physical parent history')
    return action


def materialize_inherited_finite_normal_phase(base_directory, output, *, span, steps,
        max_iterations=20, repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve prior applications')
    if not np.isfinite(span) or span<=0 or type(steps)is not int or steps<1:
        raise ValueError('forward child span and positive cells required')
    base=load_finite_normal_endpoint(base_directory,side='outgoing',repository=root)
    with np.load(base['source']/'application.npz',allow_pickle=False) as f:
        pair=f['updated_raw_pair'].copy();reference=f['reference_raw_pair'].copy()
    rep=base['representation'];P=base['coordinates']['lift'];n=base['coordinates']['x_count'];params=base['receipt']['action_parameters']
    refs=dict(base['input_hashes'])
    for name in ('muon_birth_inherited_finite_normal_phase','muon_birth_finite_normal_trace_graph',
                 'muon_birth_finite_normal_phase','muon_birth_phase_continuation'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    evaluate=lambda eta,t:inherited_child_finite_normal_action(P@eta,t,pair,reference,rep,**params)
    eta=base['master'];a0=evaluate(eta,0.);x=eta[:n].copy();p=a0['gradient'][n:2*n].copy();p0=p.copy();h=span/steps
    out.mkdir(parents=True);stages=[];contacts=[];times=[]
    for k in range(steps):
        time=(k+.5)*h;callback=lambda e: evaluate(e,time)
        def checkpoint(iteration,z,a,scale,history,status):
            path=out/'checkpoints'/f'stage_{k:04d}'/f'accepted_{iteration:04d}';path.mkdir(parents=True)
            _compressed_npz(path/'application.npz',dict(incoming_x=x,incoming_p=p,stage_guess=eta,
                unknowns=z,residual=a['residual'],jacobian=a['jacobian'],row_scale=scale,
                midpoint_independent_raw=P@a['midpoint_coefficients']))
            md=dict(scope='INHERITED_PROFILE_CHILD_PHASE_ACCEPTED_CHECKPOINT',stage=k,iteration=iteration,
                status=status,coordinate_time=time,span=span,steps=steps,input_hashes=refs,action_parameters=params,
                history=history,numerical_sha256=sha256((path/'application.npz').read_bytes()).hexdigest(),
                resume_scope='Saved exact accepted unknowns, incoming canonical pair and same action clock; resume implementation must pin these inputs.')
            (path/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
        s=solve_phase_midpoint(x,p,eta,h,callback,max_iterations=max_iterations,checkpoint=checkpoint)
        stages.append(s);contacts.append(discrete_action_cotangents(s['application'],h));times.append(time)
        if s['status']!='REPRESENTED_PHASE_TOLERANCE':break
        a=s['application'];x=a['x_new'].copy();p=a['p_new'].copy();eta=np.r_[x,a['v_mid'],a['y_mid']]
    apps=[s['application'] for s in stages]
    arrays=dict(initial_pair=pair,reference_pair=reference,initial_independent_raw=base['raw'],initial_p=p0,
        x_final=x,p_final=p,coordinate_lift=P,stage_coordinate_time=np.array(times),
        stage_independent_raw=np.array([P@a['midpoint_coefficients'] for a in apps]),
        stage_unknowns=np.array([s['unknowns'] for s in stages]),
        stage_action_gradient=np.array([a['action']['gradient'] for a in apps]),
        stage_action_hessian=np.array([a['action']['hessian'] for a in apps]),
        stage_residual=np.array([a['residual'] for a in apps]),stage_jacobian=np.array([a['jacobian'] for a in apps]),
        stage_row_scale=np.array([s['row_scale'] for s in stages]),
        stage_profile_increment=np.array([a['action']['inherited_profile_increment'] for a in apps]),
        stage_wall_profile=np.array([a['action']['inherited_wall_profile'] for a in apps]),
        stage_wall_gauge=np.array([a['action']['wall_gauge'] for a in apps]),
        stage_wall_gauge_rate=np.array([a['action']['wall_gauge_rate'] for a in apps]),
        stage_initial_face=np.array([c['initial_face'] for c in contacts]),
        stage_final_face=np.array([c['final_face'] for c in contacts]))
    _compressed_npz(out/'application.npz',arrays)
    if refs!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('action owner changed during application')
    md=dict(classification='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION',side='outgoing',span=span,steps=steps,
        completed_steps=sum(s['status']=='REPRESENTED_PHASE_TOLERANCE' for s in stages),
        stages=[dict(status=s['status'],scaled_residual=s['scaled_residual'],history=s['history']) for s in stages],
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),action_parameters=params,
        all_multiplier_and_Gauss_rows_retained=True,source_image_projected=False,
        initial_inherited_profile_norm=float(np.linalg.norm(a0['inherited_profile_increment'])),
        initial_wall_image_norm=float(np.linalg.norm(a0['inherited_wall_profile'])),
        canonical_initial_defects=[float(np.linalg.norm(c['initial_face']+s['incoming_p'])) for c,s in zip(contacts,stages)],
        canonical_final_defects=[float(np.linalg.norm(c['final_face']-a['p_new'])) for c,a in zip(contacts,apps)],
        computational_clock_scope='parent/reference first germs are affine coordinate lifts; child coefficients are solved; no E0 history or physical duration selected',
        raw_loader_guard='independent raw268 omits the explicitly saved unprojected profile; native consumers must use the full wall/profile image and its jets',
        supersession='repairs omission of the inherited child profile in muon_birth_finite_normal_phase outgoing applications; preserved old runs remain diagnostics',
        physical_formation_cutoff_or_Pauli_selected=False,
        error_scope='binary64 analytic action and exact Jacobian; numerical domain/trial error and action rounding are not enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--span',type=float,required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--max-iterations',type=int,default=20)
    a=p.parse_args();print(json.dumps(materialize_inherited_finite_normal_phase(a.base_directory,a.output,span=a.span,steps=a.steps,max_iterations=a.max_iterations),sort_keys=True))
