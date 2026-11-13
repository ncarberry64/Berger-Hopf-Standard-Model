"""Compose the two actual boundary actions on a common three-trace graph.

The two attachment traces are glued before their stationarity equations
are solved. All other field/algebraic responses were already retained in
the consumed arm operators. This conditional proper-normal trace graph
is not the temporal event-domain formation operator or a local R/c.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_phase_continuation import _compressed_npz


def common_normal_boundary_form(incoming, child, incoming_inertia, child_inertia,
                                *, incoming_lapse, child_lapse):
    """Solve shared attachment stationarity with unit common normal trace.

    C maps (a0,a1,n) to (a0,a1,n,a0,a1,n). Hence F=C^T diag(P,C) C=P+C.
    Its two attachment equations are solved together. No independent
    attachment minima, resistance eigenline, or positive form is assumed.
    Source matrices retain their original nonsymmetric rounding contacts.
    """
    matrices=[np.asarray(x)for x in (incoming,child,incoming_inertia,child_inertia)]
    if any(not np.isrealobj(x)or x.shape!=(3,3)or not np.isfinite(x).all()for x in matrices):
        raise ValueError('four finite real same-three-trace forms required')
    if not np.isfinite([incoming_lapse,child_lapse]).all()or min(incoming_lapse,child_lapse)<=0:
        raise ValueError('each arm actual positive proper clock density required')
    parent,child,Ip,Ic=[x.astype(float)for x in matrices]
    F=parent+child
    phi=np.r_[-np.linalg.solve(F[:2,:2],F[:2,2]),1.]
    residual=(F@phi)[:2]
    parent_value=float(phi@parent@phi);child_value=float(phi@child@phi)
    return dict(common_form=F,common_trace_lift=phi,
        incoming_trace_lift=phi.copy(),child_trace_lift=phi.copy(),
        attachment_stationarity_residual=residual,
        quadratic_attachment_derivative=((F+F.T)@phi)[:2],
        form_antisymmetric_rounding=F-F.T,
        incoming_signed_action_pairing=parent_value,
        child_signed_action_pairing=child_value,
        negative_incoming_drive_pairing=-parent_value,
        combined_signed_action_pairing=parent_value+child_value,
        direct_combined_pairing=float(phi@F@phi),
        incoming_proper_inertia_on_common_trace=float(incoming_lapse*(phi@Ip@phi)),
        child_proper_inertia_on_common_trace=float(child_lapse*(phi@Ic@phi)),
        common_normal_amplitude=1.,attachment_block_condition=float(np.linalg.cond(F[:2,:2])),
        attachment_trace_gluing='common two attachment coefficients before stationarity; common unit proper-normal trace is the explicit conditional domain',
        local_R_or_physical_i_r_drive_c_selected=False)


def materialize_common_normal_boundary(incoming_boundary,child_boundary,output,*,repository=ROOT):
    """Consume complete preserved arm applications rather than input forms."""
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier common trace applications')
    inputs=[];refs={}
    for path,side in zip((incoming_boundary,child_boundary),('incoming','outgoing')):
        p=Path(path);p=p if p.is_absolute()else root/p
        b=(p/'result.json').read_bytes();r=json.loads(b);data=(p/'application.npz').read_bytes()
        if r['classification']!='EVALUATED_REPAIRED_FULL_FIELD_PROPER_NORMAL_BOUNDARY_APPLICATION'or r['side']!=side:
            raise ValueError('actual complete signed parent/child boundary applications required')
        if sha256(data).hexdigest()!=r['numerical_sha256']:raise ValueError('boundary arrays changed')
        refs.update(r['input_hashes'])
        for name in ('result.json','application.npz'):refs[(p/name).relative_to(root).as_posix()]=sha256((p/name).read_bytes()).hexdigest()
        with np.load(p/'application.npz',allow_pickle=False)as z:
            inputs.append(dict(receipt=r,mixed=z['mixed_response'].copy(),kinetic=z['kinetic_response'].copy(),
                arm_independent_attachment_normal_lift=z['fixed_far_canonical_covector_normal_trace_lift'].copy()))
    parent,child=inputs
    a=common_normal_boundary_form(parent['mixed'],child['mixed'],parent['kinetic'],child['kinetic'],
        incoming_lapse=parent['receipt']['induced_lapse'],child_lapse=child['receipt']['induced_lapse'])
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)}
    for side,x in zip(('incoming','outgoing'),inputs):
        arrays[side+'_mixed_form']=x['mixed'];arrays[side+'_kinetic_form']=x['kinetic']
        arrays[side+'_separately_eliminated_attachment_normal_lift']=x['arm_independent_attachment_normal_lift']
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    for name in ('muon_common_normal_boundary_form','muon_birth_finite_geometric_trace_endpoint'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    if refs!={p:sha256((root/p).read_bytes()).hexdigest()for p in refs}:raise RuntimeError('consumed action changed')
    md={k:v for k,v in a.items()if not isinstance(v,np.ndarray)}
    md.update(classification='EVALUATED_SHARED_ATTACHMENT_PROPER_NORMAL_BOUNDARY_ACTION',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        attachment_stationarity_residual_max=float(np.max(abs(a['attachment_stationarity_residual']))),
        quadratic_attachment_derivative_max=float(np.max(abs(a['quadratic_attachment_derivative']))),
        antisymmetric_rounding_max=float(np.max(abs(a['form_antisymmetric_rounding']))),
        common_trace_lift=a['common_trace_lift'].tolist(),
        separately_eliminated_arm_normal_sum=sum(x['receipt']['attachment_eliminations']['fixed_far_canonical_covector']['normal_response']for x in inputs),
        temporal_orientation='parent-final +Pi and child-initial -Pi; each form differentiates positive chronological arm action',
        far_face_scope='fixed recorded numerical canonical covectors, coordinates free; outer faces are not identified with E0/final child',
        inherited_field_images_internal_responses_and_original_y_rows_retained=True,
        proper_normal_common_graph_not_claimed_to_replace_full_temporal_reset=True,
        physical_formation_or_cutoff_or_Pauli_selected=False,
        error_scope='binary64 contraction and shared trace solve on preserved complete finite arm action forms; no producer/domain uncertainty enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('incoming-boundary','child-boundary','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_common_normal_boundary(a.incoming_boundary,a.child_boundary,a.output),sort_keys=True))
