"""Named gauge-Ward quotient of the true-birth paired mean application.

The two identities follow from the literal simultaneous variation
delta At=theta, delta Ar_dot=theta_r, delta H_dot=-G_Y H theta_wall.
They retain the scalar trace contact. All original birth rows and their
compatibility residuals are exported; no singular vectors select rows.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import qr

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_attached_phase import load_attached_endpoint
from .muon_birth_paired_field_endpoint import endpoint_layout
from .muon_trace_enriched_charged_current_response import enriched_central_profiles
from .muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from .muon_magnetic_birth_mean_rows import weighted_row_surjection
from .muon_birth_phase_continuation import _compressed_npz


def named_birth_ward_relations(raw_pair,action_gradients,action_hessians,representation,base_residual):
    """Return both source-owned row relations and their off-shell contacts.

    theta.(GaussP-GaussC)+theta_r.jump(pAr)
    -(G_Y H_P).jump(pH)+(G_Y.T pH_C).trace(H)=0.
    Differentiating the coefficients adds D_L.base_residual, which is
    retained even at the numerically corrected endpoint.
    """
    raw=np.asarray(raw_pair,float);g=np.asarray(action_gradients,float);H=np.asarray(action_hessians,float)
    layout=endpoint_layout(representation);nr=layout['raw_count'];na=len(layout['At']);nd=len(layout['dynamic']);hs=layout['H_start']
    count=2*(25+na)+2*nd+8+2
    residual=np.asarray(base_residual,float)
    if raw.shape!=(2,nr) or g.shape!=raw.shape or H.shape!=(2,nr,nr) or residual.shape!=(count,):
        raise ValueError('complete two-arm same-action birth arrays required')
    profiles=enriched_central_profiles(representation);theta=profiles['theta_coefficients'];dr=profiles['radial_derivative_coefficients']
    one=25+na;traceH=2*one+2*nd;jumpH=traceH+4;L=np.zeros((2,count));contact=np.zeros((2,2*nr))
    for j,i in enumerate(layout['At']):
        label=representation['gauge_labels'][i]
        if label['internal']==3:
            L[:,24+j]=theta[label['radial']];L[:,one+24+j]=-theta[label['radial']]
    for j,i in enumerate(layout['dynamic']):
        label=representation['gauge_labels'][i]
        if label['field']=='A_rho' and label['internal']==3:L[:,2*one+nd+j]=dr[label['radial']]
    G=higgs_u2_real_representation()['real_generators'][3]
    L[:,traceH:traceH+4]=G.T@g[1,hs+4:hs+8]
    L[:,jumpH:jumpH+4]=-G@raw[0,hs:hs+4]
    contact[:,hs:hs+4]=-G.T@residual[jumpH:jumpH+4]
    contact[:,nr:]=(G@residual[traceH:traceH+4])@H[1,hs+4:hs+8]
    return dict(row_relations=L,off_shell_coefficient_contact=contact,
        relation_equation='theta.(GaussP-GaussC)+theta_r.jump(pAr)-(G_Y H_P).jump(pH)+(G_Y.T pH_C).trace(H)=0',
        generator_G_Y=G,theta_coefficients=theta,theta_radial_coefficients=dr,
        scalar_trace_contact_retained=True,numerical_singular_vectors_used=False)


def _arb_named_row_application(J0,f0,r0,w0,B0,*,precision_bits=160):
    """Outward source solve on the named quotient, retaining original rows."""
    from flint import arb,arb_mat,ctx
    previous=ctx.prec;ctx.prec=precision_bits
    try:
        J=arb_mat(J0.tolist());f=arb_mat(f0.tolist());B=arb_mat(B0.tolist())
        r=arb_mat(np.diag(r0).tolist());iw=arb_mat(np.diag(1/w0).tolist())
        A=B*r*J*iw;rhs=-B*r*f;dual=(A*A.transpose()).solve(rhs)
        normalized=A.transpose()*dual;correction=iw*normalized;original=J*correction+f
        if not all(dual[i,j].is_finite() for i in range(dual.nrows()) for j in range(dual.ncols())):
            raise ArithmeticError('named quotient full row inverse was not certified')
        upper=lambda a:max((float(np.nextafter(float(abs(a[i,j]).upper()),np.inf))
            for i in range(a.nrows()) for j in range(a.ncols())),default=0.)
        def export(a):
            mid=np.array([[float(a[i,j].mid()) for j in range(a.ncols())] for i in range(a.nrows())])
            err=np.array([[float(np.nextafter(float(abs(a[i,j]-arb(float(mid[i,j]))).upper()),np.inf))
                for j in range(a.ncols())] for i in range(a.nrows())])
            return mid,err
        delta,error=export(correction)
        return dict(correction=delta,correction_export_error_upper=error,
            certificate=dict(precision_bits=precision_bits,named_quotient_full_row_inverse_certified=True,
                quotient_equation_residual_upper=upper(B*r*original),original_all_row_residual_upper=upper(original),
                original_scaled_all_row_residual_upper=upper(r*original),
                exact_input_convention='stored binary64 J,source,row/coordinate scales and named QR row basis interpreted exactly; quotient assembly and least-norm solve use Arb',
                physical_action_rounding_or_continuum_error_enclosed=False))
    finally:ctx.prec=previous


def named_ward_mean_application(jacobian,source,row_scale,coefficient_weights,ward_relations,*,certify=True):
    """Solve the complete independent Ward-row quotient and retain all rows."""
    J=np.asarray(jacobian,float);f=np.asarray(source,float);r=np.asarray(row_scale,float);w=np.asarray(coefficient_weights,float)
    L=np.asarray(ward_relations,float)
    if L.shape!=(2,len(J)) or np.linalg.matrix_rank(L)!=2:raise ValueError('two independent named action Ward relations required')
    # The scaling moves a relation L.f=0 to (L/r).(r*f)=0.
    Q,R=qr((L/r[None,:]).T,mode='full');B=Q[:,2:].T
    A=B@(r[:,None]*J/w[None,:]);rhs=np.einsum('ij,j...->i...',B,r.reshape((-1,)+(1,)*(f.ndim-1))*f)
    a=weighted_row_surjection(A,rhs,np.ones(len(A)),np.ones(J.shape[1]))
    delta=a['correction']/w.reshape((-1,)+(1,)*(f.ndim-1))
    certificate={}
    if certify:
        bound=_arb_named_row_application(J,f.reshape(len(J),-1),r,w,B)
        delta=bound['correction'].reshape(delta.shape);error=bound['correction_export_error_upper'].reshape(delta.shape)
        certificate=bound['certificate']
    else:error=np.zeros_like(delta)
    residual=np.einsum('ij,j...->i...',J,delta)+f
    return dict(correction=delta,correction_export_error_upper=error,original_residual=residual,
        original_scaled_residual=r.reshape((-1,)+(1,)*(f.ndim-1))*residual,
        named_source_compatibility=np.einsum('ij,j...->i...',L,f),
        named_original_row_compatibility=np.einsum('ij,j...->i...',L,residual),
        row_basis=B,normalized_null_basis=a['normalized_null_basis'],
        row_factor_condition_number=a['row_factor_condition_number'],named_ward_relation_count=2,
        literal_original_row_count=len(J),independent_named_quotient_row_count=len(A),
        numerical_spectral_directions_removed=0,stored_action_arithmetic_certificate=certificate,
        physical_E0_or_moving_mean_graph_selected=False)


def retained_named_birth_mean_application(mean_directory,*,repository=ROOT):
    root=Path(repository);folder=Path(mean_directory);folder=folder if folder.is_absolute() else root/folder
    b=(folder/'result.json').read_bytes();receipt=json.loads(b)
    if receipt['classification']!='EVALUATED_TRUE_BIRTH_PAIRED_MEAN_ROW_APPLICATION_FIXED_REFERENCE':
        raise ValueError('actual source-driven true birth mean application required')
    refs=dict(receipt['input_hashes'])
    for p,h in refs.items():
        if sha256((root/p).read_bytes()).hexdigest()!=h:raise ValueError('consumed source owner changed: '+p)
    archive=folder/'application.npz';data=archive.read_bytes()
    if sha256(data).hexdigest()!=receipt['numerical_sha256']:raise ValueError('birth paired source application changed')
    with np.load(archive,allow_pickle=False) as a:arrays={k:a[k].copy() for k in a.files}
    refs[folder.relative_to(root).as_posix()+'/result.json']=sha256(b).hexdigest();refs[archive.relative_to(root).as_posix()]=sha256(data).hexdigest()
    matches=[p for p in refs if 'paired_attachment_endpoint_' in p and p.endswith('/result.json')]
    if len(matches)!=1:raise ValueError('unique same-action true birth endpoint required')
    endpoint=load_attached_endpoint((root/matches[0]).parent,side='incoming',repository=root)
    with np.load(endpoint['source']/'application.npz',allow_pickle=False) as a:
        raw=a['updated_raw_pair'];grad=a['updated_gradients'];hess=a['updated_hessians'];base_residual=a['updated_residual']
    ward=named_birth_ward_relations(raw,grad,hess,endpoint['representation'],base_residual)
    J=arrays['jacobian'];free=arrays['free_indices'];r=arrays['row_scale'];w=arrays['coefficient_weights']
    a=named_ward_mean_application(J[:,free],arrays['source'],r,w,ward['row_relations'])
    full=np.zeros((2*len(raw[0]),8,8));full[free]=a['correction']
    a.update(raw_mean_correction=full.reshape(2,len(raw[0]),8,8),input_hashes=refs,ward=ward,
        literal_ward_jacobian_defect=ward['row_relations']@J+ward['off_shell_coefficient_contact'],
        literal_ward_base_residual=ward['row_relations']@base_residual,
        source=arrays['source'],source_application_receipt=receipt)
    return a


def materialize_named_birth_mean_application(mean_directory,output,*,repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute() else root/out
    if out.exists():raise FileExistsError('preserve earlier Ward/source applications')
    a=retained_named_birth_mean_application(mean_directory,repository=root);out.mkdir(parents=True)
    arrays={k:v for k,v in a.items() if isinstance(v,np.ndarray)}
    arrays.update({'ward_'+k:v for k,v in a['ward'].items() if isinstance(v,np.ndarray)})
    _compressed_npz(out/'application.npz',arrays);refs=dict(a['input_hashes'])
    for name in ('muon_magnetic_birth_ward_mean','muon_magnetic_birth_mean_rows',
        'muon_trace_enriched_charged_current_response','muon_intrinsic_higgs_gauge_action'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    md=dict(classification='EVALUATED_NAMED_GAUGE_WARD_TRUE_BIRTH_MEAN_APPLICATION',input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        ward_equation=a['ward']['relation_equation'],scalar_trace_contact_retained=True,
        literal_ward_jacobian_defect_max=float(np.max(abs(a['literal_ward_jacobian_defect']))),
        literal_ward_base_residual_max=float(np.max(abs(a['literal_ward_base_residual']))),
        named_source_compatibility_max=float(np.max(abs(a['named_source_compatibility']))),
        original_all_row_residual_norm=float(np.linalg.norm(a['original_residual'])),
        original_scaled_all_row_residual_norm=float(np.linalg.norm(a['original_scaled_residual'])),
        row_factor_condition_number=a['row_factor_condition_number'],raw_mean_correction_norm=float(np.linalg.norm(a['raw_mean_correction'])),
        named_ward_relation_count=2,literal_original_row_count=220,independent_named_quotient_row_count=218,
        numerical_spectral_directions_removed=0,stored_action_arithmetic_certificate=a['stored_action_arithmetic_certificate'],
        numerical_particular_selection='minimum coefficient-weight norm in the source-owned Ward-row quotient; original220 rows and full null space retained',
        geometric_mean_scope=a['source_application_receipt']['geometric_mean_scope'],
        moving_affine_trace_scope=a['source_application_receipt']['moving_affine_trace_scope'],
        physical_E0_or_moving_mean_graph_selected=False,physical_formation_or_native_Pauli_completed=False)
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mean-directory',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args();print(json.dumps(materialize_named_birth_mean_application(args.mean_directory,args.output),sort_keys=True))
