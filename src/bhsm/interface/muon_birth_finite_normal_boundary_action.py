"""Complete finite normal boundary applications on the repaired phases.

Incoming-final and child-initial temporal orientations are retained.
Internal trace fields and all algebraic equations are solved, including
the two attachment traces when their action block is invertible.  The
resulting endpoint DtN is not a local restoring density or selected c.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_chronological_boundary_action import discrete_boundary_two_jet
from .muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from .muon_birth_chronological_normal_boundary_response import full_birth_trace_response, mixed_canonical_far_response
from .muon_birth_phase_continuation import _compressed_npz


def eliminate_attachment_traces(response):
    """Eliminate two internal attachment amplitudes, retaining unit normal."""
    R=np.asarray(response,float)
    if R.shape!=(3,3) or not np.isfinite(R).all():raise ValueError('complete three-trace action form required')
    attachment=-np.linalg.solve(R[:2,:2],R[:2,2]);lift=np.r_[attachment,1.]
    residual=(R@lift)[:2]
    return dict(normal_response=float(lift@R@lift),trace_lift=lift,
        attachment_stationarity_residual=residual,attachment_block_condition=float(np.linalg.cond(R[:2,:2])),
        attachment_traces_eliminated_not_discarded=True)


def load_completed_finite_normal_cell(folder, *, repository=ROOT):
    root=Path(repository);path=Path(folder);path=path if path.is_absolute()else root/path
    b=(path/'result.json').read_bytes();r=json.loads(b)
    if r['steps']!=1 or r['completed_steps']!=1 or r['stages'][0]['status']!='REPRESENTED_PHASE_TOLERANCE':
        raise ValueError('one fully converged chronological cell required')
    refs=dict(r['input_hashes'])
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    data=(path/'application.npz').read_bytes()
    if sha256(data).hexdigest()!=r['numerical_sha256']:raise ValueError('saved phase values changed')
    with np.load(path/'application.npz',allow_pickle=False)as a:arrays={k:a[k].copy()for k in a.files}
    if r['side']=='outgoing':
        if r['classification']!='EVALUATED_INHERITED_PROFILE_CHILD_CANONICAL_ACTION' or r['source_image_projected']:
            raise ValueError('outgoing cell must retain its unprojected inherited profile')
        raw=arrays['stage_independent_raw'][0]
        base=r['input_hashes']
        source=next(p.rsplit('/',1)[0]for p in base if p.endswith('/finite_moving_trace_run_1/result.json'))
    else:
        raw=arrays['stage_midpoint_raw'][0];source=r['consumed_base']
    loaded=load_finite_normal_endpoint(source,side=r['side'],repository=root)
    refs[path.relative_to(root).as_posix()+'/result.json']=sha256(b).hexdigest()
    refs[path.relative_to(root).as_posix()+'/application.npz']=sha256(data).hexdigest()
    return dict(receipt=r,arrays=arrays,raw=raw,representation=loaded['representation'],input_hashes=refs)


def finite_normal_boundary_application(folder, *, repository=ROOT):
    """Apply all original fields to the proper normal boundary trace."""
    base=load_completed_finite_normal_cell(folder,repository=repository);r=base['receipt'];a=base['arrays'];rep=base['representation']
    H=a['stage_action_hessian'][0];g=a['stage_action_gradient'][0]
    n=(len(H)-40)//2;h=abs(r['span']);face=int(r['side']=='incoming')
    boundary=discrete_boundary_two_jet(H,g,h,n)
    kinetic=true_legendre_normal_trial(H,base['raw'],rep)
    response=full_birth_trace_response(boundary['hessian'],n,face,
        kinetic['trial_trace'],kinetic['literal_gauge_generators'][:n],frame='radial')
    mixed=mixed_canonical_far_response(H,h,face,kinetic,rep)
    attachment={name:eliminate_attachment_traces(value['response'])for name,value in
        (('kinetic',kinetic),('fixed_far_coordinate',response),('fixed_far_canonical_covector',mixed))}
    attachment['kinetic']['normal_proper_clock_inertia']=kinetic['induced_lapse']*attachment['kinetic']['normal_response']
    expected=np.r_[a['stage_initial_face'][0],a['stage_final_face'][0]]
    if r['span']<0:expected=np.r_[-a['stage_final_face'][0],-a['stage_initial_face'][0]]
    return dict(base=base,kinetic=kinetic,boundary=boundary,response=response,mixed=mixed,
        eliminated_attachment_applications=attachment,temporal_contact_reconstruction=boundary['gradient'][:2*n]-expected,
        birth_face=face,dynamic_count=n,proper_clock=kinetic['induced_lapse'],
        recorded_far_covector=boundary['gradient'][(1-face)*n:(2-face)*n],
        endpoint_DtN_is_local_R=False,physical_c_or_formation_selected=False)


def materialize_finite_normal_boundary(folder,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier boundary applications')
    a=finite_normal_boundary_application(folder,repository=root);r=a['base']['receipt'];arrays={}
    for name in ('kinetic','boundary','response','mixed'):
        arrays.update({name+'_'+key:value for key,value in a[name].items()if isinstance(value,np.ndarray)})
    for name,b in a['eliminated_attachment_applications'].items():
        arrays[name+'_normal_trace_lift']=b['trace_lift'];arrays[name+'_attachment_residual']=b['attachment_stationarity_residual']
    arrays.update(raw_independent_midpoint=a['base']['raw'],temporal_contact_reconstruction=a['temporal_contact_reconstruction'],
        recorded_far_covector=a['recorded_far_covector'])
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    refs=dict(a['base']['input_hashes'])
    for name in ('muon_birth_finite_normal_boundary_action','muon_birth_chronological_boundary_action',
        'muon_birth_chronological_normal_inertia','muon_birth_chronological_normal_boundary_response'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    md=dict(classification='EVALUATED_REPAIRED_FULL_FIELD_PROPER_NORMAL_BOUNDARY_APPLICATION',side=r['side'],
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        normal_coordinate_time_inertia=a['kinetic']['normal_coordinate_time_inertia'],
        normal_proper_clock_inertia=a['kinetic']['normal_proper_clock_inertia'],induced_lapse=a['proper_clock'],
        full_original_kinetic_y_defect=float(np.max(abs(a['kinetic']['full_algebraic_residual']))),
        literal_gauge_Ward_image_max=float(np.max(abs(a['kinetic']['gauge_Ward_image']))),
        temporal_contact_reconstruction_max=float(np.max(abs(a['temporal_contact_reconstruction']))),
        birth_face=a['birth_face'],dynamic_count=a['dynamic_count'],algebraic_count=40,
        fixed_far_response=a['response']['response'].tolist(),mixed_far_response=a['mixed']['response'].tolist(),
        attachment_eliminations={name:{key:value for key,value in b.items()if not isinstance(value,np.ndarray)}
            for name,b in a['eliminated_attachment_applications'].items()},
        complete_birth_response_defect=float(np.max(abs(a['response']['solve_residual']))),
        balanced_complete_birth_response_defect=float(np.max(abs(a['response']['scaled_solve_residual']))),
        original_full_birth_y_defect=float(np.max(abs(a['response']['original_algebraic_residual']))),
        mixed_response_defect=float(np.max(abs(a['mixed']['solve_residual']))),
        balanced_mixed_response_defect=float(np.max(abs(a['mixed']['scaled_solve_residual']))),
        recorded_far_covector_norm=float(np.linalg.norm(a['recorded_far_covector'])),
        internal_field_image_retained=True,true_Lyy_all_Gauss_and_constraint_rows_retained=True,
        temporal_orientation='incoming-final +Pi; child-initial -Pi; positive chronological action on each cell',
        far_face_scope='two explicit numerical applications: fixed far coordinate or fixed recorded canonical covector; neither is identified as E0/finalchild',
        endpoint_DtN_is_local_restoring_density=False,physical_r_i_drive_c_or_Pauli_selected=False,
        area_coefficient_scope='same gamma(c) area application remains coupled to base and physical restoring-domain response; no gamma0 selected',
        error_scope='Binary64 complete action-block solves; no action-rounding or continuum bound. The integrated endpoint form cannot be inserted as local R into c=I/R.')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    x=p.parse_args();print(json.dumps(materialize_finite_normal_boundary(x.phase_directory,x.output),sort_keys=True))
