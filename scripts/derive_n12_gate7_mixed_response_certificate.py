"""Consume frozen mixed eigenline; enclose physical response and norm jets.

The normalized descriptor Hessian is deliberately not inferred from the
98 physical-state components. Source contractions retain one shared domain.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,fmpq,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_mixed_eigenline_certificate as base
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.shared_implicit_response_jet import dot,matvec,solve_with_operator
from bhsm.interface.shared_positive_norm_jet import normalize


def setup(evidence,work):
    inherited=ROOT/'artifacts/flagship_integration/gate7_mixed_eigenline_20260923'
    certificate=json.loads((inherited/'certificate.json').read_bytes())
    repeat=json.loads((inherited/'reproduction.json').read_bytes())
    if not repeat['byte_identical'] or base.sha(inherited/'certificate.json')!=repeat['first_SHA256']:
        raise ValueError('new mixed eigenline must already be independently reproduced')
    s=base.operands(evidence,work);old=s['domain']
    groups=list(old.groups)+[(287,349,'box')];d=TaylorDomain(groups,349)
    lift=lambda v:base.unmodel(d,base.model(v))
    for key in ('state','u','v','moving'):s[key]=[lift(v) for v in s[key]]
    s['domain']=d
    s['psi_u']=[base.unmodel(d,v) for v in certificate['first_psi_u_models']]
    s['psi_v']=[base.swap(v) for v in s['psi_u']]
    s['lambda_u']=base.unmodel(d,certificate['first_lambda_u_model']);s['lambda_v']=base.swap(s['lambda_u'])
    s['psi_uv']=[base.unmodel(d,v) for v in certificate['psi_uv_models']]
    s['lambda_uv']=base.unmodel(d,certificate['lambda_uv_model'])
    value=evidence/'artifacts/flagship_integration/.affine_physical_value_pilot_work/endpoint_019'
    vh=json.loads((value/'record.json').read_bytes());vr=json.loads((value/'reproduction.json').read_bytes())
    normpath=evidence/'artifacts/flagship_integration/.coupled_normalized_physical_value_work/endpoint_019/record.json'
    nh=json.loads(normpath.read_bytes())
    if not vr['byte_identical'] or not vh['report']['validation_passed'] or not nh['report']['positive_physical_G_norm']:
        raise ValueError('frozen response and positive normalization certificates required')
    paths=[value/'record.json',value/'reproduction.json',value/'value.npz',normpath,inherited/'certificate.json',
           inherited/'reproduction.json',Path(__file__),ROOT/'src/bhsm/interface/shared_positive_norm_jet.py']
    weights_path=base.action.ENDPOINT.with_suffix('.npz')
    axispath=ROOT/'artifacts/action_extension/BHSM_AE4_CURRENT_C2_GREEN_IMAGE_PARTITION_RECONCILIATION.npz'
    paths.extend([weights_path,axispath])
    s['sources'].update({str(p.resolve()):base.sha(p) for p in paths})
    if s['sources'][str((value/'value.npz').resolve())]!=vh['data_SHA256'] or s['sources'][str((value/'record.json').resolve())]!=vr['record_SHA256']:
        raise ValueError('new response import hashes do not reconcile')
    with np.load(value/'value.npz',allow_pickle=False) as z:
        q0,A,res0,qbox=[base.read_array(z,k) for k in ('response_center','signed_response_derivatives','response_center_residual','response_box')]
    eigpath=evidence/'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_019/eigenpair.npz'
    with np.load(eigpath,allow_pickle=False) as z:V=base.read_array(z,'trial_1_variation_bounds')
    alpha=arb(fmpq(vh['report']['response_bound']['weighted_error_upper_rational']))
    rL,rT=[arb(fmpq(v)) for v in s['radius_exact']];R=s['preconditioner']
    dy=[v-v.c for v in s['moving']]
    eigen_rhs=[dy[-1]*q0[i]-dy[i]*q0[-1] for i in range(61)]+[-dot(dy[:61],list(q0[:61]))]
    eigen_res=matvec([[R[i,j] for j in range(62)] for i in range(62)],eigen_rhs)
    response=[]
    for i in range(62):
        sign=-1 if i==61 else 1
        co=[sign*A[i,j]*(rL if j==0 else rT) for j in range(75)]+[arb(0)]*274
        value_model=d.affine(q0[i]+sign*res0[i],co)+eigen_res[i]
        a=value_model.a.entries();a[287+i]=(V[i]*alpha+value_model.r).upper()
        response.append(d.affine(value_model.c,a))
    s['response']=response;s['frozen_response_box']=qbox
    # Import the second saved solve: its last coordinate is the physical b_u.
    df=evidence/'artifacts/flagship_integration/.coupled_endpoint_uniform_df_work/endpoint_019'
    dh=json.loads((df/'record.json').read_bytes())
    with np.load(df/'derivative.npz',allow_pickle=False) as z:pre=base.read_array(z,'preconditioned_variation_rhs')[1]
    aa=[]
    for batch in dh['report']['coupled_inverse_bounds']:
        aa.extend(arb(fmpq(p['weighted_error_upper_rational'])) for p in batch['solve_bounds'][1])
    with np.load(weights_path,allow_pickle=False) as z:
        weights=[arb(float(v)) for v in z['state_weights']];sc=arb(float(z['independent_signed_descriptors'][19]))
    coeff=arb_mat(62,98,[(pre[i,j]+arb(0,(V[i]*aa[j]).upper()))*(-1 if i==61 else 1) for i in range(62) for j in range(98)])
    rawmap=arb_mat(98,75,[weights[i]*s['state'][i].a[0,j] for i in range(98) for j in range(75)])
    first=coeff*rawmap
    s['response_u']=[d.affine(0,[arb(0)]*75+[first[i,j] for j in range(75)]+[arb(0)]*199) for i in range(62)]
    s['response_v']=[base.swap(v) for v in s['response_u']]
    with np.load(axispath,allow_pickle=False) as z:raw=z['current_center_green_image_unit_mid']
    axes=raw[1:]/np.linalg.norm(raw[1:],axis=1)[:,None]
    ds=[arb(0)]*349;ds[0]=arb(float(axes[18,73]))*arb(float(base.action.TRIAL_DESCRIPTOR_SCALE))*rL
    ds[74]=arb(float(base.action.TRIAL_DESCRIPTOR_SCALE))*rT
    s['descriptor']=d.affine(sc,ds)
    su=[arb(0)]*349;su[75:150]=ds[:75]
    s['descriptor_u']=d.affine(0,su);s['descriptor_v']=base.swap(s['descriptor_u'])
    s['normalization_lower']=arb(fmpq(nh['report']['physical_G_norm_lower_rational']))
    s['norm_header_SHA256']=base.sha(normpath)
    receipt=dict(source_input_hashes=s['sources'],inherited_receipt=s['inherited_operand_receipt'],
        mixed_eigenline_certificate_SHA256=repeat['first_SHA256'],parameters=349,groups=d.groups,
        radius_exact=s['radius_exact'],original_domain_unchanged=True)
    rp=work/'immutable_inputs.json';data=base.encode(receipt)
    if rp.exists():
        if rp.read_bytes()!=data:raise ValueError('physical response input receipt changed')
    else:
        pending=rp.with_suffix('.pending');pending.write_bytes(data);os.replace(pending,rp)
    return s


def run(evidence,work,out):
    ctx.prec=512;work.mkdir(parents=True,exist_ok=True)
    s=setup(evidence,work);d=s['domain'];evaluate=base.Evaluator(s,work)
    psi=s['moving'][:61];lam=s['moving'][-1];u,v=s['u'],s['v']
    pu,pv,puv=s['psi_u'],s['psi_v'],s['psi_uv']
    lu,lv,luv=s['lambda_u'],s['lambda_v'],s['lambda_uv']
    response,qu,qv=s['response'],s['response_u'],s['response_v'];h=response[:61];b=response[-1]
    hu,hv=qu[:61],qv[:61];bu,bv=qu[-1],qv[-1]
    qw,rw,_,_=base.action.metric_data();qw=[arb(float(w)) for w in qw];rw=[arb(float(w)) for w in rw]
    weights_path=base.action.ENDPOINT.with_suffix('.npz')
    with np.load(weights_path,allow_pickle=False) as z:w=[arb(float(v)) for v in z['state_weights']]
    c=[qw[i]*s['state'][37+i] for i in range(37)]
    cu=[qw[i]*u[37+i] for i in range(37)];cv=[qw[i]*v[37+i] for i in range(37)]
    zero=d.affine(0);pad=lambda z:[zero]*37+list(z)
    craw=[c[i]/w[i] for i in range(37)]+[zero]*61
    curaw=[cu[i]/w[i] for i in range(37)]+[zero]*61
    cvraw=[cv[i]/w[i] for i in range(37)]+[zero]*61
    guv=evaluate.gradient([u,v])
    gcuv=evaluate.gradient([craw,u,v])
    gcu_v=evaluate.gradient([curaw,v]);gcv_u=evaluate.gradient([cvraw,u])
    ghuv=evaluate.gradient([pad(h),u,v])
    ghv_u=evaluate.gradient([pad(hv),u]);ghu_v=evaluate.gradient([pad(hu),v])
    Fuv=[(rw[i]*qw[i]*guv[i]/w[i] if i<37 else zero)
         -rw[i]/w[37+i]*(gcuv[37+i]+gcu_v[37+i]+gcv_u[37+i]) for i in range(61)]
    rhs=[Fuv[i]-ghuv[37+i]-ghv_u[37+i]-ghu_v[37+i]+luv*h[i]+lu*hv[i]+lv*hu[i]
         -puv[i]*b-pu[i]*bv-pv[i]*bu for i in range(61)]
    rhs.append(-dot(puv,h)-dot(pu,hv)-dot(pv,hu))
    def apply_K(z):
        gz=evaluate.gradient([pad(z[:61])])
        return [gz[37+i]-lam*z[i]+psi[i]*z[-1] for i in range(61)]+[dot(psi,z[:61])]
    mixed,proof=solve_with_operator(rhs,apply_K,s['preconditioner'],s['weights'],s['q'])
    huv,buv=mixed[:61],mixed[-1]
    orthogonal=dot(psi,huv)+dot(pu,hv)+dot(pv,hu)+dot(puv,h)
    if not orthogonal.enclosure().contains(0):raise ArithmeticError('mixed response normalization contradiction')
    scalar,su,sv=s['descriptor'],s['descriptor_u'],s['descriptor_v']
    N=[scalar*x for x in c]+[rw[i]*(b*psi[i]+scalar*h[i]) for i in range(61)]
    Nu=[su*c[i]+scalar*cu[i] for i in range(37)]+[
        rw[i]*(bu*psi[i]+b*pu[i]+su*h[i]+scalar*hu[i]) for i in range(61)]
    Nv=[sv*c[i]+scalar*cv[i] for i in range(37)]+[
        rw[i]*(bv*psi[i]+b*pv[i]+sv*h[i]+scalar*hv[i]) for i in range(61)]
    Nuv=[su*cv[i]+sv*cu[i] for i in range(37)]+[
        rw[i]*(buv*psi[i]+bu*pv[i]+bv*pu[i]+b*puv[i]+su*hv[i]+sv*hu[i]+scalar*huv[i]) for i in range(61)]
    normalized=normalize(N,Nu,Nv,Nuv,s['normalization_lower'])
    payload=dict(algorithm='SHARED_ORIGINAL_DOMAIN_MIXED_RESPONSE_AND_NORM_V1',endpoint=19,
        radius_exact=s['radius_exact'],parameters=d.dimension,groups=d.groups,original_domain_unchanged=True,
        same_shared_u_v_parameters=True,independent_coordinate_domain_substitution=False,
        inherited_response_values_and_first_variations_reused=True,point_Hessian_recomputed=False,
        first_variation_semantics='Saved physical-response solve (second variation block); last coordinate is b_u. It is not an eigenvalue derivative.',
        primal_response_models=[base.model(v) for v in response],
        response_u_models=[base.model(v) for v in qu],response_v_by_exact_u_v_permutation=True,
        response_uv_models=[base.model(v) for v in mixed],
        physical_response_h_uv_norm_upper=base.number(base.norm(huv,w[37:])),
        physical_response_b_uv_absolute_upper=base.number(buv.support()),
        complete_mixed_response_rhs_models=[base.model(v) for v in rhs],
        bordered_predictor_preconditioned_residual_models=[base.model(v) for v in proof['preconditioned_residual_models']],
        weighted_correction_upper=base.number(proof['weighted_correction_upper']),
        reused_inverse_defect_upper=base.number(s['q']),
        mixed_orthogonality_residual_model=base.model(orthogonal),mixed_orthogonality_residual_contains_zero=True,
        physical_numerator_models=[base.model(v) for v in N],
        physical_numerator_u_models=[base.model(v) for v in Nu],physical_numerator_v_by_exact_u_v_permutation=True,
        physical_numerator_uv_models=[base.model(v) for v in Nuv],
        norm_model=base.model(normalized['norm']),norm_u_model=base.model(normalized['norm_u']),
        norm_v_model=base.model(normalized['norm_v']),norm_uv_model=base.model(normalized['norm_uv']),
        positive_norm_lower=base.number(s['normalization_lower']),
        inherited_positive_norm_certificate_SHA256=s['norm_header_SHA256'],
        normalized_98_state_mixed_models=[base.model(v) for v in normalized['physical_mixed']],
        normalized_98_state_mixed_norm_upper=base.number(base.norm(normalized['physical_mixed'])),
        norm_uv_absolute_upper=base.number(normalized['norm_uv'].support()),
        descriptor_model=base.model(scalar),descriptor_u_model=base.model(su),descriptor_v_by_exact_u_v_permutation=True,
        descriptor_incidence='s=s0+scale*(rL*axis[19,73]*theta0+rT*theta74), from the original frozen augmented frame',
        source_SHA256=s['sources'],immutable_inputs_SHA256=base.sha(work/'immutable_inputs.json'),
        inherited_operand_receipt=s['inherited_operand_receipt'],new_contraction_receipts=evaluate.receipts,
        normalization_derived_from_same_N_equation=True,independent_normalization_error_budget_added=False,
        mixed_physical_response_enclosed=True,positive_normalization_mixed_enclosed=True,
        normalized_descriptor_mixed_enclosed=False,complete_99_component_physical_Hessian_enclosed=False,
        first_missing_operator='D_uv delta = D_uv [b*S3[p,p,a] + s*S3[p,p,d]]; then f99_uv=(delta_uv-nu_uv*f99-nu_u*f99_v-nu_v*f99_u)/nu',
        Gate7_closed=False,kappa_L=None,kappa_T=None,new_physical_budget_debit=False,FULL_BHSM_COMPLETE=False)
    with out.open('xb') as f:f.write(base.encode(payload))
    print(json.dumps({k:payload[k] for k in ('physical_response_h_uv_norm_upper','physical_response_b_uv_absolute_upper',
        'normalized_98_state_mixed_norm_upper','norm_uv_absolute_upper','mixed_physical_response_enclosed','positive_normalization_mixed_enclosed')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.work.resolve(),a.out.resolve())
