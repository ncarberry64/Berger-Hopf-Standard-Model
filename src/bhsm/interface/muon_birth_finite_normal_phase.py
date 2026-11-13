"""Canonical continuation of the evaluated finite anchored normal chart.

The consumed base has active geometry and a nonlinear normalized response.
Every multiplier/Gauss row remains in the temporal action.  Its finite
outer canonical face is an output, not the physical E0 boundary graph.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import enriched_representation_from_values
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action
from .muon_exact_material_response import exact_geometric_connection_coefficient_jets
from .muon_birth_phase_continuation import phase_continuation, discrete_action_cotangents, _compressed_npz
from .muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from .muon_parent_maxwell_full_weak import full_maxwell_weak_geometric_jets
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_parent_retarded_hypercharge import WALL


def area_length_coefficient(c, alpha_fsc, worldvolume_dimension):
    """Owner gamma(c), with its first two derivatives; no EM calibration."""
    if not np.isfinite(c) or c <= 0 or not np.isfinite(alpha_fsc) or alpha_fsc <= 0:
        raise ValueError('positive explicit length-squared and FSC primitive required')
    if type(worldvolume_dimension) is not int or worldvolume_dimension < 1:
        raise ValueError('actual stratum worldvolume dimension required')
    p = -worldvolume_dimension/2
    gamma = alpha_fsc*c**p
    return dict(value=gamma, first=p*gamma/c, second=p*(p-1)*gamma/c**2,
                formula='gamma=alpha_FSC*c^(-m/2)', alpha_EM_substituted=False)


def proper_clock_normal_density(coordinate_inertia, local_coordinate_stiffness, lapse):
    """Convert an ALREADY derived local normal density at a frozen clock.

    S2=1/2 int dt (I_t a_t^2-R_t a^2), d tau=l dt:
    I_tau=l I_t and R_tau=R_t/l.  An integrated endpoint Schur is not
    accepted as a local stiffness by this helper's contract.
    """
    if not np.isfinite(lapse) or lapse <= 0:
        raise ValueError('positive induced proper clock required')
    return dict(inertia=lapse*coordinate_inertia,
                stiffness=local_coordinate_stiffness/lapse,
                local_density_only=True, integrated_endpoint_Schur_is_resistance=False)


def load_finite_normal_endpoint(folder, *, side, repository=ROOT):
    root=Path(repository);source=Path(folder);source=source if source.is_absolute() else root/source
    if side not in ('incoming','outgoing'):raise ValueError('incoming or outgoing arm required')
    b=(source/'result.json').read_bytes();receipt=json.loads(b)
    if (receipt['status']!='REPRESENTED_MOVING_TRACE_TOLERANCE'
            or receipt['source_profile_projected']):
        raise ValueError('consume solved unprojected finite moving-trace base')
    refs=dict(receipt['input_hashes'])
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed action changed: '+p)
    data=(source/'application.npz').read_bytes()
    if sha256(data).hexdigest()!=receipt['numerical_sha256']:raise ValueError('base values changed')
    with np.load(source/'application.npz',allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
    rep=enriched_representation_from_values(receipt,arrays)
    raw=arrays['updated_raw_pair'][int(side=='outgoing')]
    c=generic_coordinate_lift(rep['gauge_labels']);master=c['lift'].T@raw
    if not np.array_equal(c['lift']@master,raw):raise ValueError('all base coefficients must survive the phase lift')
    refs[(source/'result.json').relative_to(root).as_posix()]=sha256(b).hexdigest()
    refs[(source/'application.npz').relative_to(root).as_posix()]=sha256(data).hexdigest()
    return dict(raw=raw,master=master,representation=rep,coordinates=c,
                receipt=receipt,source=source,input_hashes=refs)


def finite_normal_wall_conormal(raw, representation):
    """Literal lateral Maxwell contact on the same exact response chart."""
    rep=representation;N=rep['gauge_count'];a,at=raw[100:100+N],raw[100+N:100+2*N]
    value=rep['wall_trace_map'][None,None];radial=rep['wall_radial_derivative_map'][None,None]
    fields=dict(gauge=np.einsum('rpfkj,j->rpfk',value,a),
        gauge_tau=np.einsum('rpfkj,j->rpfk',value,at),
        gauge_rho=np.einsum('rpfkj,j->rpfk',radial,a),gauge_angular=np.zeros((1,1,3,5,4)))
    tests=np.moveaxis(value,-1,1);tr=np.moveaxis(radial,-1,1)
    geo=exact_geometric_connection_coefficient_jets(12,raw[:37],raw[37:74],raw[74:98],
        np.array([WALL]),source_value=raw[98],source_rate=raw[99])
    weak=full_maxwell_weak_geometric_jets(geo,np.ones(1),np.ones(1),**fields,
        tests=tests,tests_tau=np.zeros_like(tests),tests_rho=tr,tests_angular=np.zeros((1,N,1,3,5,4)))
    return MAXWELL_TO_CAP*weak['radial_momentum_test']['values']


def materialize_finite_normal_phase(base_directory, output, *, side, span, steps,
        max_iterations=10, repository=ROOT, resume_checkpoint=None):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve earlier phase applications')
    if (side=='incoming' and span>=0) or (side=='outgoing' and span<=0):
        raise ValueError('incoming past / outgoing future from birth0 required')
    initial=load_finite_normal_endpoint(base_directory,side=side,repository=root)
    rep=initial['representation'];P=initial['coordinates']['lift'];n=initial['coordinates']['x_count']
    params=dict(initial['receipt']['action_parameters'])
    evaluate=lambda eta:pointwise_finite_normal_action(P@eta,rep,**params)
    refs=dict(initial['input_hashes'])
    for name in ('muon_birth_finite_normal_phase','muon_birth_finite_normal_trace_graph',
                 'muon_exact_material_response','muon_birth_chronological_normal_inertia',
                 'muon_birth_phase_continuation'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    eta=initial['master'];a0=evaluate(eta);p0=a0['gradient'][n:2*n]
    x_start=eta[:n];p_start=p0;guess_start=eta;start_stage=0;resume={};resume_hash=None
    if resume_checkpoint is not None:
        path=Path(resume_checkpoint);path=path if path.is_absolute() else root/path
        cb=(path/'result.json').read_bytes();cr=json.loads(cb)
        if (cr['input_hashes']!=refs or (cr['side'],cr['span'],cr['steps'])!=(side,span,steps)):
            raise ValueError('resume must preserve exact action, numerical basis and signed temporal cells')
        if sha256((path/'application.npz').read_bytes()).hexdigest()!=cr['numerical_sha256']:
            raise ValueError('accepted checkpoint values changed')
        with np.load(path/'application.npz',allow_pickle=False) as a:
            x_start=a['incoming_x'];p_start=a['incoming_p'];guess_start=a['stage_guess']
            resume=dict(resumed_unknowns=a['unknowns'],resumed_row_scale=a['row_scale'],resumed_iteration=cr['iteration'])
        start_stage=cr['stage'];resume_hash=sha256(cb).hexdigest()
    out.mkdir(parents=True)
    def checkpoint(stage,iteration,z,a,scale,history,status,x,p,guess):
        path=out/'checkpoints'/f'stage_{stage:04d}'/f'accepted_{iteration:04d}';path.mkdir(parents=True)
        _compressed_npz(path/'application.npz',dict(incoming_x=x,incoming_p=p,stage_guess=guess,
            unknowns=z,residual=a['residual'],jacobian=a['jacobian'],row_scale=scale,
            midpoint_raw=P@a['midpoint_coefficients']))
        md=dict(scope='FINITE_NORMAL_PHASE_ACCEPTED_CHECKPOINT',stage=stage,iteration=iteration,
            status=status,side=side,span=span,steps=steps,history=history,input_hashes=refs,
            numerical_sha256=sha256((path/'application.npz').read_bytes()).hexdigest(),
            resume_argv=['C:/Python314/python.exe','-m','bhsm.interface.muon_birth_finite_normal_phase',
                '--base-directory',str(initial['source']),'--output','CHOOSE_NEW_OUTPUT_DIRECTORY',
                '--side',side,'--span',str(span),'--steps',str(steps),'--max-iterations',str(max_iterations),
                '--resume-checkpoint',str(path)],resume_environment=dict(PYTHONPATH='src'))
        (path/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    result=phase_continuation(x_start,p_start,guess_start,span,steps,evaluate,max_iterations=max_iterations,
        checkpoint=checkpoint,start_stage=start_stage,**resume)
    stages=result['applications'];apps=[s['application'] for s in stages]
    contacts=[discrete_action_cotangents(a,result['step']) for a in apps]
    raws=[P@a['midpoint_coefficients'] for a in apps]
    normals=[true_legendre_normal_trial(a['action']['hessian'],raw,rep) for a,raw in zip(apps,raws)]
    arrays=dict(initial_raw=initial['raw'],initial_master=eta,initial_p=p0,
        x_final=result['x_final'],p_final=result['p_final'],coordinate_lift=P,
        stage_unknowns=np.array([s['unknowns'] for s in stages]),stage_midpoint_raw=np.array(raws),
        stage_action_hessian=np.array([a['action']['hessian'] for a in apps]),
        stage_action_gradient=np.array([a['action']['gradient'] for a in apps]),
        stage_residual=np.array([a['residual'] for a in apps]),stage_jacobian=np.array([a['jacobian'] for a in apps]),
        stage_row_scale=np.array([s['row_scale'] for s in stages]),
        stage_initial_face=np.array([a['initial_face'] for a in contacts]),
        stage_final_face=np.array([a['final_face'] for a in contacts]),
        lateral_wall_conormals=np.array([finite_normal_wall_conormal(raw,rep) for raw in raws]),
        proper_normal_traces=np.array([a['proper_normal_trace'] for a in normals]),
        normal_velocity_algebraic_lifts=np.array([a['velocity_algebraic_lift'] for a in normals]))
    _compressed_npz(out/'application.npz',arrays)
    if refs!={p:sha256((root/p).read_bytes()).hexdigest() for p in refs}:raise RuntimeError('owner changed during phase production')
    md=dict(classification='EVALUATED_NONLINEAR_ANCHORED_NORMAL_PHASE_AND_PROPER_CLOCK_WEAK_ROWS',
        side=side,span=span,steps=steps,completed_steps=result['completed_steps'],
        resumed_stage=start_stage,resumed_checkpoint_sha256=resume_hash,
        consumed_base=initial['source'].relative_to(root).as_posix(),input_hashes=refs,
        action_parameters=params,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        stages=[dict(status=s['status'],scaled_residual=s['scaled_residual'],history=s['history']) for s in stages],
        normal_forms=[dict(coordinate_time_inertia=a['normal_coordinate_time_inertia'],
            proper_clock_inertia=a['normal_proper_clock_inertia'],induced_lapse=a['induced_lapse'],
            proper_normal_projection=a['normal_chart_projection_factor'],
            full_y_equation_defect=float(np.max(abs(a['full_algebraic_residual']))),
            gauge_Ward_image_max=float(np.max(abs(a['gauge_Ward_image']))),
            solve_defect=float(np.max(abs(a['solve_residual'])))) for a in normals],
        canonical_initial_defects=[float(np.linalg.norm(c['initial_face']+s['incoming_p'])) for c,s in zip(contacts,stages)],
        canonical_final_defects=[float(np.linalg.norm(c['final_face']-a['p_new'])) for c,a in zip(contacts,apps)],
        all_multiplier_and_Gauss_rows_retained=True,normal_profile_normalization_exact=True,
        outer_face_role='finite chronological output canonical covector; not identified with E0 or a physical finalchild condition',
        integrated_endpoint_Schur_is_local_restoring_coefficient=False,
        area_family_equation='gamma=alpha_FSC*c^(-m/2), c=i/r; endpoint correction and formation/clock operator must be recomputed together',
        physical_formation_cutoff_or_Pauli_selected=False,
        error_scope='binary64 analytic action/Jacobian and numerical canonical correction; no physical domain, action rounding or continuum enclosure')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--side',choices=('incoming','outgoing'),required=True);p.add_argument('--span',type=float,required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--max-iterations',type=int,default=10);p.add_argument('--resume-checkpoint',type=Path)
    a=p.parse_args();print(json.dumps(materialize_finite_normal_phase(a.base_directory,a.output,side=a.side,span=a.span,steps=a.steps,max_iterations=a.max_iterations,resume_checkpoint=a.resume_checkpoint),sort_keys=True))
