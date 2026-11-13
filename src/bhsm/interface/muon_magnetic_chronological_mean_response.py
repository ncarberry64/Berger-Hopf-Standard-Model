"""Actual source-driven mean propagation from the true birth correction.

Each arm receives its own same-action canonical birth covector.  The
incoming past application is the exact coordinate reversal L(x,-v),
Pi_reverse=-Pi_future; it does not reverse physical source-rate data.
The finite past face is retained as an output, never identified with E0.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_chronological_boundary_action import retained_chronological_boundary_application
from .muon_birth_inhomogeneous_canonical_mean import inhomogeneous_canonical_step
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_birth_phase_continuation import _compressed_npz


def mean_birth_canonical_state(raw_mean,raw_hessian,raw_mean_cotangent,coordinate_lift,dynamic_count):
    """Use the total canonical dual H_v.delta_eta+g_v exactly once."""
    delta=np.asarray(raw_mean,float);H=np.asarray(raw_hessian,float);g=np.asarray(raw_mean_cotangent,float);P=np.asarray(coordinate_lift,float);n=int(dynamic_count)
    if delta.shape!=g.shape or H.shape!=(len(delta),len(delta)) or P.shape[0]!=len(delta) or P.shape[1]<=2*n:
        raise ValueError('same raw mean, literal action Hessian/source and full x/v/y lift required')
    total=np.einsum('ij,j...->i...',H,delta)+g
    x=np.einsum('ij,i...->j...',P[:,:n],delta)
    p=np.einsum('ij,i...->j...',P[:,n:2*n],total)
    y=np.einsum('ij,i...->j...',P[:,2*n:],total)
    return dict(canonical_state=np.concatenate((x,p)),algebraic_constitutive_defect=y,
        momentum_source_count=1,canonical_pairing='same action coefficient dual; no second scalar2Re, Gram or measure')


def past_directed_canonical_mean(action_hessian,positive_span,mean_cotangent,birth_state,frame_covectors=None):
    """Exact reverse-coordinate action, returning future-oriented fields."""
    s=np.asarray(birth_state,float);n=len(s)//2;H=np.asarray(action_hessian,float);g=np.asarray(mean_cotangent,float)
    sign=np.ones(len(H));sign[n:2*n]=-1
    reverse_state=s.copy();reverse_state[n:]*=-1
    reverse=inhomogeneous_canonical_step(sign[:,None]*H*sign[None,:],positive_span,
        sign.reshape((-1,)+(1,)*(g.ndim-1))*g,reverse_state,frame_covectors)
    final=reverse['final_canonical_state'].copy();final[n:]*=-1
    lift=sign.reshape((-1,)+(1,)*(g.ndim-1))*reverse['midpoint_velocity_algebraic_lift']
    return dict(far_canonical_state=final,future_midpoint_velocity_algebraic_lift=lift,
        reverse_coordinate_application=reverse,
        orientation_rule='u=-future_time; L_reverse(x,v_u,y)=L_future(x,-v_u,y); Pi_u=-Pi_future; source Qdot stays the owned future derivative before coordinate pullback')


def _read_packet(folder,root,classification,*,json_name='result.json',archive_name='application.npz'):
    path=Path(folder);path=path if path.is_absolute() else root/path;b=(path/json_name).read_bytes();r=json.loads(b)
    if r['classification']!=classification:raise ValueError('required source/action classification differs')
    refs=dict(r['input_hashes'])
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed owner changed: '+p)
    a=path/archive_name;data=a.read_bytes();expected=r.get('numerical_sha256',r.get('archive',{}).get('sha256'))
    if sha256(data).hexdigest()!=expected:raise ValueError('consumed numerical packet changed')
    with np.load(a,allow_pickle=False) as saved:arrays={k:saved[k].copy() for k in saved.files}
    refs[(path/json_name).relative_to(root).as_posix()]=sha256(b).hexdigest();refs[a.relative_to(root).as_posix()]=sha256(data).hexdigest()
    return r,arrays,refs


def retained_magnetic_chronological_mean_response(birth_mean_directory,midpoint_load_directory,*,repository=ROOT):
    root=Path(repository)
    birth,means,refs=_read_packet(birth_mean_directory,root,'EVALUATED_NAMED_GAUGE_WARD_TRUE_BIRTH_MEAN_APPLICATION')
    midpoint,loads,more=_read_packet(midpoint_load_directory,root,
        'EVALUATED_TOTAL_RAW268_CUBIC_MEAN_LOAD_FROM_FRESH_SAME_PHASE_RESPONSES',json_name='mean_load.json',archive_name='mean_load.npz')
    for p,h in more.items():
        if p in refs and refs[p]!=h:raise ValueError('birth and midpoint consumed different owners')
        refs[p]=h
    sources=[p for p in refs if '/muon_magnetic_true_birth_mean_load_' in p and p.endswith('/result.json')]
    if len(sources)!=1:raise ValueError('unique true-E1 contact source required')
    _,true,extra=_read_packet((root/sources[0]).parent,root,
        'EVALUATED_TRUE_E1_MAGNETIC_CUBIC_CANONICAL_CONSTRAINT_ENERGY_CONTACTS');refs.update(extra)
    outputs={}
    for side in ('incoming','outgoing'):
        candidates=[p for p in refs if p.endswith('/result.json') and 'attached_phase_'+side+'_' in p]
        if len(candidates)!=1:raise ValueError('unique same-arm chronological phase required')
        a=retained_chronological_boundary_application((root/candidates[0]).parent,repository=root)
        if a['receipt']['steps']!=1:raise ValueError('source receipt owns precisely one actual midpoint cell')
        if not np.array_equal(a['raw_chronological_midpoints'][0],loads[side+'_raw268']):raise ValueError('source mean and chronological action differ')
        rep=a['representation'];c=generic_coordinate_lift(rep['gauge_labels']);P=c['lift'];n=c['x_count'];arm=0 if side=='incoming' else 1
        phase=a['receipt'];endpoint=load_attached_endpoint(phase['consumed_paired_endpoint_path'],side=side,repository=root,
            radial_points=phase['radial_points'],cap_points=phase['cap_points'])
        if not np.array_equal(endpoint['raw'],true[side+'_raw_fields']):raise ValueError('true E1 source and phase initial endpoint differ')
        with np.load(endpoint['source']/'application.npz',allow_pickle=False) as saved:Hbirth=saved['updated_hessians'][arm]
        state=mean_birth_canonical_state(means['raw_mean_correction'][arm],Hbirth,true[side+'_raw_mean_cotangent'],P,n)
        g=np.einsum('ij,iab->jab',P,loads[side+'_raw_mean_cotangent'])
        D=enriched_central_profiles(rep)['radial_derivative_coefficients']
        Ar=[j for j,i in enumerate(c['dynamic_gauge_indices']) if rep['gauge_labels'][i]['field']=='A_rho' and rep['gauge_labels'][i]['internal']==3]
        C=np.zeros((2,n));C[:,38+np.array(Ar)]=D.T
        H=a['action_hessians'][0];h=a['signed_step']
        if side=='incoming':
            response=past_directed_canonical_mean(H,h,g,state['canonical_state'],C)
            far=response['far_canonical_state'];lift=response['future_midpoint_velocity_algebraic_lift'];application=response['reverse_coordinate_application']
            orientation=response['orientation_rule']
        else:
            application=inhomogeneous_canonical_step(H,h,g,state['canonical_state'],C)
            far=application['final_canonical_state'];lift=application['midpoint_velocity_algebraic_lift']
            orientation='positive future coordinate time from child birth0; canonical momentum and physical Qdot carried with their owned orientation'
        raw_mean=np.einsum('ij,jab->iab',P,lift)
        outputs[side]=dict(birth_canonical_state=state['canonical_state'],
            birth_algebraic_constitutive_defect=state['algebraic_constitutive_defect'],
            future_raw_midpoint_mean=raw_mean,far_canonical_state=far,application=application,
            raw_midpoint=a['raw_chronological_midpoints'][0],coordinate_lift=P,mean_master_cotangent=g,
            signed_future_displacement=-h if side=='incoming' else h,orientation_rule=orientation)
    outputs.update(input_hashes=refs,birth_mean_receipt=birth,
        mean_source_role='actual full action/source-motion paired load; birth canonical source retained once',
        past_face_role='output of the finite incoming prefix; no E0 or far canonical boundary condition selected',
        physical_full_moving_birth_graph_or_stationary_mean_closed=False)
    return outputs


def materialize_magnetic_chronological_mean_response(birth_mean_directory,midpoint_load_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve previous chronological means')
    a=retained_magnetic_chronological_mean_response(birth_mean_directory,midpoint_load_directory,repository=root)
    arrays={};rows={}
    for side in ('incoming','outgoing'):
        r=a[side];arrays.update({side+'_'+k:v for k,v in r.items() if isinstance(v,np.ndarray)})
        arrays.update({side+'_application_'+k:v for k,v in r['application'].items() if isinstance(v,np.ndarray)})
        rows[side]=dict(signed_future_displacement=r['signed_future_displacement'],orientation_rule=r['orientation_rule'],
            raw_midpoint_mean_norm=float(np.linalg.norm(r['future_raw_midpoint_mean'])),
            birth_canonical_state_norm=float(np.linalg.norm(r['birth_canonical_state'])),far_canonical_state_norm=float(np.linalg.norm(r['far_canonical_state'])),
            birth_algebraic_constitutive_defect_max=float(np.max(abs(r['birth_algebraic_constitutive_defect']))),
            original_algebraic_defect_max=float(np.max(abs(r['application']['original_algebraic_defect']))),
            frame_reaction_norm=float(np.linalg.norm(r['application']['frame_reactions'])),
            stored_action_arithmetic_certificate=r['application']['stored_action_arithmetic_certificate'])
    refs=dict(a['input_hashes'])
    for name in ('muon_magnetic_chronological_mean_response','muon_magnetic_birth_ward_mean',
        'muon_birth_inhomogeneous_canonical_mean','muon_birth_chronological_boundary_action'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    md=dict(classification='EVALUATED_TRUE_BIRTH_SOURCE_DRIVEN_CHRONOLOGICAL_MEAN_APPLICATION',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),applications=rows,
        mean_source_role=a['mean_source_role'],past_face_role=a['past_face_role'],momentum_source_count=1,
        physical_full_moving_birth_graph_or_stationary_mean_closed=False,
        physical_formation_or_native_Pauli_completed=False,
        geometric_birth_mean_scope=a['birth_mean_receipt']['geometric_mean_scope'],
        native_consumer='future_raw_midpoint_mean is the same-background raw268 direction for the induced D_Gamma mean contraction; direct two insertions and overlap remain separate',
        error_scope='Arb certifies exact stored cell/source/derived birth-state arithmetic; upstream birth export rounding and directional Dg step-halving errors are not propagated as rigorous bounds')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--birth-mean-directory',required=True,type=Path);p.add_argument('--midpoint-load-directory',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args();print(json.dumps(materialize_magnetic_chronological_mean_response(args.birth_mean_directory,args.midpoint_load_directory,args.output),sort_keys=True))
