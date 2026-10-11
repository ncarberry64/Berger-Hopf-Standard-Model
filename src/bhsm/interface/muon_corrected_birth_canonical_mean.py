"""Canonical initial means from the actual corrected moving birth graph.

The child momentum includes its inherited parent mixed Hessian. The
primitive parent and joint constraint defects remain separate outputs.
The explicit affine parent mean can be applied at every phase node.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_corrected_birth_mean import BASE
from .muon_birth_finite_normal_phase import load_finite_normal_endpoint
from .muon_birth_finite_geometric_trace_endpoint import pair_master_chart
from .muon_birth_finite_normal_trace_graph import pointwise_finite_normal_action,finite_normal_trace_graph_action_two_jet
from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from .muon_birth_phase_continuation import _compressed_npz


def affine_mean_lift(raw_count,coordinate_time):
    """Derivative of the exact existing affine first-germ chart, not an ODE."""
    if raw_count<100 or not np.isfinite(coordinate_time):raise ValueError('complete first germ and finite time required')
    A=np.eye(raw_count);A[:37,37:74]+=coordinate_time*np.eye(37);A[98,99]+=coordinate_time
    return A


def joint_birth_canonical_means(raw_delta,parent_hessian,graph_hessian,joint_source,incoming_source,coordinate_lift):
    """Actual p_mean=H_v delta+g_v, with the child cross-arm term once."""
    d=np.asarray(raw_delta,float);H=np.asarray(graph_hessian,float);P=np.asarray(coordinate_lift,float)
    nr=len(P);nm=P.shape[1];n=(nm-40)//2
    if d.shape[:2]!=(2,nr)or H.shape!=(2*nr,2*nr)or parent_hessian.shape!=(nr,nr):
        raise ValueError('complete actual joint graph and primitive parent Hessian required')
    g=np.asarray(joint_source,float);gp=np.asarray(incoming_source,float)
    if g.shape!=d.shape or gp.shape!=d[0].shape:raise ValueError('same paired source columns required')
    parent=np.einsum('ij,j...->i...',parent_hessian,d[0])+gp
    child_own=np.einsum('ij,j...->i...',H[nr:,nr:],d[1])+g[1]
    inherited=np.einsum('ij,j...->i...',H[nr:,:nr],d[0])
    child=child_own+inherited
    canonical=[];algebraic=[]
    for arm,total in enumerate((parent,child)):
        x=np.einsum('ij,i...->j...',P[:,:n],d[arm]);p=np.einsum('ij,i...->j...',P[:,n:2*n],total)
        canonical.append(np.r_[x,p]);algebraic.append(np.einsum('ij,i...->j...',P[:,2*n:],total))
    return dict(canonical_states=np.array(canonical),primitive_constitutive_algebraic_defects=np.array(algebraic),
        incoming_total_raw_cotangent=parent,outgoing_total_raw_cotangent=child,
        outgoing_own_mean_raw_cotangent=child_own,outgoing_inherited_parent_raw_cotangent=inherited,
        momentum_source_count=1,child_parent_cross_count=1)


def inherited_parent_mean_gradient(raw_child,coordinate_time,initial_pair,reference_pair,
        representation,initial_parent_mean,*,nu_squared_action,surface_gamma=None):
    """Actual child L-gradient forcing from the inherited affine parent mean.

    The reference chart is held fixed. This is a mixed Hessian application
    of the existing full graph; it retains all density, profile and scalar
    wall contacts and is distinct from the odd-source D3 mean cotangent.
    """
    t=float(coordinate_time);raw=np.asarray(initial_pair,float)
    mean=np.asarray(initial_parent_mean,float);A=affine_mean_lift(raw.shape[1],t)
    if mean.shape[0]!=raw.shape[1]:raise ValueError('same raw parent mean coefficients required')
    pair=np.array([affine_geometry_germ(raw[0],t),raw_child])
    ref=np.array([affine_geometry_germ(x,t)for x in reference_pair])
    graph=finite_normal_trace_graph_action_two_jet(pair,ref,representation,
        nu_squared_action=nu_squared_action,surface_gamma=surface_gamma)
    nr=len(raw_child);P=pair_master_chart(representation)['one_lift']
    shifted=np.einsum('ij,j...->i...',A,mean)
    g=np.einsum('ij,j...->i...',graph['raw_hessian'][nr:,:nr],shifted)
    return dict(raw_gradient_forcing=g,master_gradient_forcing=np.einsum('ij,i...->j...',P,g),
        parent_mean_at_time=shifted,affine_parent_mean_map=A,
        scope='existing affine parent/reference germ, all child action rows; no physical parent history selection')


def materialize_corrected_birth_canonical_mean(mean_directory,output,*,repository=ROOT):
    root=Path(repository);folder=Path(mean_directory);folder=folder if folder.is_absolute()else root/folder
    out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve previous canonical mean applications')
    data=(folder/'result.json').read_bytes();md=json.loads(data)
    if md['classification']!='EVALUATED_CORRECTED_TRUE_MOVING226_BIRTH_SECOND_MEAN':raise ValueError('current moving226 mean required')
    refs=dict(md['input_hashes']);archive=folder/'application.npz'
    if sha256(archive.read_bytes()).hexdigest()!=md['numerical_sha256']:raise ValueError('birth mean changed')
    refs[(folder/'result.json').relative_to(root).as_posix()]=sha256(data).hexdigest()
    refs[archive.relative_to(root).as_posix()]=md['numerical_sha256']
    with np.load(archive,allow_pickle=False)as a:means={k:a[k].copy()for k in a.files}
    endpoint=load_finite_normal_endpoint(BASE,side='incoming',repository=root);rep=endpoint['representation']
    refs.update(endpoint['input_hashes']);raw=means['base_updated_raw_pair'];reference=means['base_reference_raw_pair']
    params=endpoint['receipt']['action_parameters'];parent=pointwise_finite_normal_action(raw[0],rep,**params)
    c=pair_master_chart(rep);P=c['one_lift']
    incoming_source=means['joint_incoming_only_fixed_raw_mean']+means['joint_source_motion_raw_mean'][0]
    result=joint_birth_canonical_means(means['raw_mean_correction'],parent['raw_hessian'],
        means['base_graph_raw_hessian'],means['joint_raw_mean'],incoming_source,P)
    arrays={k:v for k,v in result.items()if isinstance(v,np.ndarray)}
    arrays.update(raw_mean_correction=means['raw_mean_correction'],initial_pair=raw,reference_pair=reference,
        coordinate_lift=P,parent_raw_hessian=parent['raw_hessian'],graph_raw_hessian=means['base_graph_raw_hessian'],
        complete_raw_mean_cotangent=means['joint_raw_mean'],incoming_primitive_raw_mean_cotangent=incoming_source,
        inherited_parent_affine_map_birth=affine_mean_lift(268,0.))
    # One actual reached future-cell midpoint forcing, for the chronological
    # consumer; all later nodes use the identical callable above.
    phasefolder=root/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1'
    pmd=json.loads((phasefolder/'result.json').read_bytes())
    with np.load(phasefolder/'application.npz',allow_pickle=False)as a:
        stage=a['stage_independent_raw'][0].copy()if 'stage_independent_raw'in a.files else None
    if stage is None:raise ValueError('actual child independent raw midpoint required')
    t=float(pmd['span'])/(2*int(pmd['steps']))
    forcing=inherited_parent_mean_gradient(stage,t,raw,reference,rep,means['raw_mean_correction'][0],**params)
    arrays.update({'midpoint_'+k:v for k,v in forcing.items()if isinstance(v,np.ndarray)})
    for name in('result.json','application.npz'):
        path=phasefolder/name;refs[path.relative_to(root).as_posix()]=sha256(path.read_bytes()).hexdigest()
    for name in('muon_corrected_birth_canonical_mean','muon_birth_inherited_finite_normal_phase'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise RuntimeError('consumed owner changed: '+p)
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    r=dict(classification='EVALUATED_CORRECTED_MOVING_BIRTH_CANONICAL_MEAN_AND_PARENT_FORCING',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        canonical_state_norms=[float(np.linalg.norm(x))for x in result['canonical_states']],
        primitive_algebraic_defect_maxima=[float(np.max(abs(x)))for x in result['primitive_constitutive_algebraic_defects']],
        outgoing_inherited_parent_cotangent_norm=float(np.linalg.norm(result['outgoing_inherited_parent_raw_cotangent'])),
        midpoint_parent_forcing_norm=float(np.linalg.norm(forcing['raw_gradient_forcing'])),
        midpoint_coordinate_time=t,canonical_g_v_count=1,inherited_parent_cross_count=1,
        parent_phase_uses_primitive_parent_action=True,
        actual_joint_birth_constraints_and_primitive_phase_constraints_distinguished=True,
        far_canonical_mean_not_E0=True,physical_chronological_stationary_mean_or_Pauli_completed=False,
        error_scope='binary64 full action Hessian applications; excludes upstream Dg/mean correction/continuum errors')
    (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return r
