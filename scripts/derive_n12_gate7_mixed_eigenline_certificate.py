"""New original-domain mixed eigenline certificate, using frozen first solves.

No point Hessian, branch, moving-value certificate or fifth-action evaluation
is run. Imported first derivatives are reconstructed from their existing
preconditioned RHS and certified defect-correction bounds. Only the missing
uniform lambda variation and mixed action contractions are evaluated.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,fmpq,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_accepted_replay_center_outward_74d as action
from bhsm.interface.shared_action_taylor import TaylorDomain,Taylor
from bhsm.interface.uniform_action_contraction import contract
from bhsm.interface.shared_action_gradient import gradient
from bhsm.interface.shared_eigenline_jet import second_variations
from bhsm.interface.shared_implicit_response_jet import dot


def encode(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def digest(v):return hashlib.sha256(encode(v)).hexdigest().upper()
def ball(v):return [str(v.mid().fmpq()),str(v.rad().fmpq())]
def restore(v):return arb(fmpq(v[0]))+arb(0,arb(fmpq(v[1])))
def number(v):
    v=v.upper();return dict(exact=str(v.fmpq()),approximate=float(v))
def model(v):return dict(c=ball(v.c),a=[[i,ball(a)] for i,a in enumerate(v.a.entries()) if not a.is_zero()],r=str(v.r.fmpq()))
def unmodel(d,v):
    a=[arb(0)]*d.dimension
    for i,value in v['a']:a[i]=restore(value)
    return d.affine(restore(v['c']),a,arb(fmpq(v['r'])))
def read_array(z,name):
    m,r=z[name+'_mid_q'],z[name+'_rad_q']
    return np.array([restore((str(a),str(b))) for a,b in zip(m.flat,r.flat,strict=True)],dtype=object).reshape(m.shape)
def swap(v):
    a=v.a.entries();a[75:150],a[150:225]=a[150:225],a[75:150]
    return v.domain.affine(v.c,a,v.r)
def norm(values,weights=None):
    if weights is None:weights=[arb(1)]*len(values)
    return sum(((w*v.support())**2 for w,v in zip(weights,values,strict=True)),arb(0)).sqrt().upper()


def operands(evidence,work):
    package=ROOT/'artifacts/flagship_integration/gate7_moving_response_20260923'
    eigen_path=package/'eigenpair.json';eigen=json.loads(eigen_path.read_bytes())
    seed_path=ROOT/'artifacts/flagship_integration/gate7_uniform_action_20260923/scalar.json'
    seed=json.loads(seed_path.read_bytes())
    data=evidence/'artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_019/eigenpair.npz'
    df=evidence/'artifacts/flagship_integration/.coupled_endpoint_uniform_df_work/endpoint_019'
    header=json.loads((df/'record.json').read_bytes());repeat=json.loads((df/'reproduction.json').read_bytes())
    binding=header['binding']['files']
    key='artifacts/flagship_integration/.affine_eigenpair_pilot_work/endpoint_019/eigenpair.npz'
    if binding[key]!=seed['source_SHA256'][str(data.resolve())]:raise ValueError('first variations and eigenpair family differ')
    if not header['report']['validation_passed'] or not repeat['byte_identical'] or not repeat['independent_recomputation']:
        raise ValueError('frozen reproduced first-variation certificate required')
    receipt_path=work/'import_receipt.json'
    if receipt_path.exists():
        receipt=json.loads(receipt_path.read_bytes())
        if receipt['record_SHA256']!=repeat['record_SHA256'] or receipt['data_SHA256']!=header['data_SHA256']:
            raise ValueError('imported dependency binding changed')
    else:
        if sha(df/'record.json')!=repeat['record_SHA256'] or sha(df/'derivative.npz')!=header['data_SHA256']:
            raise ValueError('imported first-variation certificate binding failed')
        receipt=dict(record_SHA256=repeat['record_SHA256'],data_SHA256=header['data_SHA256'],
            path=str(df.resolve()),inherited_independent_reproduction=True,scientific_calculation_repeated=False)
        receipt_path.write_bytes(encode(receipt))
    with np.load(data,allow_pickle=False) as z:
        center,directions,R,w,V=[read_array(z,k) for k in ('center_state','affine_directions','preconditioner','trial_1_radii','trial_1_variation_bounds')]
    weights_path=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_AUGMENTED_FIXED_DESCRIPTOR_NEWTON_ENDPOINT_CANDIDATE.npz'
    with np.load(weights_path,allow_pickle=False) as z:weights=[arb(float(v)) for v in z['state_weights']]
    groups=[g for s in (0,75,150) for g in ((s,s+1,'interval'),(s+1,s+75,'euclidean'))]+[(225,287,'box')]
    d=TaylorDomain(groups,287);rL,rT=[arb(fmpq(v)) for v in eigen['radius_exact']]
    scaled=[[directions[i,j]*(rL if j==0 else rT) for j in range(75)] for i in range(98)]
    state=[d.affine(center[i],scaled[i]+[arb(0)]*212) for i in range(98)]
    u=[d.affine(0,[arb(0)]*75+scaled[i]+[arb(0)]*137) for i in range(98)]
    v=[swap(t) for t in u]
    moving=[]
    for i in range(62):
        co=[restore(p) for p in eigen['coefficients'][i]]+[arb(0)]*212
        co[225+i]=arb(fmpq(eigen['remainder_upper'][i]['exact']))
        moving.append(d.affine(restore(eigen['center'][i]),co))
    # Frozen solve: z=R*b+E*z, |z|<=w*alpha. Thus signed R*b plus V*alpha
    # encloses the solution. This is an import/algebraic conversion, not a solve.
    with np.load(df/'derivative.npz',allow_pickle=False) as z:pre=read_array(z,'preconditioned_variation_rhs')[0]
    alpha=[]
    for batch in header['report']['coupled_inverse_bounds']:
        alpha.extend(arb(fmpq(p['weighted_error_upper_rational'])) for p in batch['solve_bounds'][0])
    if len(alpha)!=99:raise ValueError('complete frozen first-variation coverage required')
    coefficients=arb_mat(61,98,[pre[i,j]+arb(0,(V[i]*alpha[j]).upper()) for i in range(61) for j in range(98)])
    rawmap=arb_mat(98,75,[weights[i]*scaled[i][j] for i in range(98) for j in range(75)])
    composed=coefficients*rawmap
    firstu=[d.affine(0,[arb(0)]*75+[composed[i,j] for j in range(75)]+[arb(0)]*137) for i in range(61)]
    RK=arb_mat(62,62,[R[i,j]*(-1 if i==61 else 1) for i in range(62) for j in range(62)])
    q=arb(fmpq(eigen['weighted_inverse_defect_upper']['exact']))
    sources={str(p.resolve()):sha(p) for p in (eigen_path,seed_path,df/'record.json',df/'reproduction.json',Path(__file__),
        ROOT/'src/bhsm/interface/shared_action_gradient.py',ROOT/'src/bhsm/interface/shared_eigenline_jet.py',
        ROOT/'src/bhsm/interface/shared_implicit_response_jet.py')}
    return dict(domain=d,state=state,u=u,v=v,moving=moving,psi_u=firstu,psi_v=[swap(t) for t in firstu],
                preconditioner=RK,weights=list(w),q=q,physical_weights=weights[37:],
                radius_exact=eigen['radius_exact'],sources=sources,import_receipt=receipt,
                inherited_operand_receipt=seed['source_SHA256'])


class Evaluator:
    def __init__(self,source,work):self.source=source;self.work=work;self.receipts=[];self.last=None
    def calculate(self,legs,all_rows):
        d=self.source['domain']
        if any(all((v.support().is_zero() if isinstance(v,Taylor) else arb(v).is_zero()) for v in leg) for leg in legs):
            return [d.affine(0)]*98 if all_rows else d.affine(0)
        payload=[[model(v if isinstance(v,Taylor) else d.affine(v)) for v in leg] for leg in legs]
        key=digest(dict(gradient=all_rows,legs=payload,sources=self.source['sources']))
        path=self.work/f'{key}.json'
        if path.exists():
            record=json.loads(path.read_bytes());values=[unmodel(d,t) for t in record['models']]
            print(json.dumps(dict(phase='RESUME_SAVED_NEW_CONTRACTION',key=key)),flush=True)
        else:
            print(json.dumps(dict(phase='NEW_ACTION_CONTRACTION',order=len(legs)+int(all_rows),gradient=all_rows,key=key)),flush=True)
            progress=lambda done,total:print(json.dumps(dict(phase='ACTION_QUADRATURE',key=key[:10],completed=done,total=total)),flush=True)
            if all_rows:values=gradient(action,self.source['state'],legs,progress)
            else:values=[contract(action,self.source['state'],legs,progress)[0]]
            record=dict(key=key,models=[model(t) for t in values])
            with path.open('xb') as f:f.write(encode(record))
        self.receipts.append(dict(key=key,SHA256=sha(path),rows=len(values)))
        return values if all_rows else values[0]
    def __call__(self,legs):return self.calculate(legs,False)
    def gradient(self,legs):
        # The two mixed third-action terms are the same function after swapping
        # the complete u/v blocks. This exact substitution preserves the domain.
        payload=[[model(v if isinstance(v,Taylor) else self.source['domain'].affine(v)) for v in leg] for leg in legs]
        if self.last is not None:
            old_legs,old_values=self.last
            permuted=[[model(swap(v)) for v in leg] for leg in old_legs]
            if payload==permuted:
                self.receipts.append(dict(exact_u_v_permutation_reused=True))
                return [swap(t) for t in old_values]
        values=self.calculate(legs,True)
        self.last=([[v if isinstance(v,Taylor) else self.source['domain'].affine(v) for v in leg] for leg in legs],values)
        return values


def run(evidence,work,out):
    ctx.prec=512;work.mkdir(parents=True,exist_ok=True)
    s=operands(evidence,work);d=s['domain'];psi=s['moving'][:61];lam=s['moving'][61]
    evaluate=Evaluator(s,work);p=[d.affine(0)]*37+psi
    # The historical projected first solve did not save lambda_u. Its auxiliary
    # border is NOT lambda_u. Compute only this missing current-domain scalar.
    lu=evaluate([p,p,s['u']]);lv=swap(lu)
    first=dict(psi_u=s['psi_u'],psi_v=s['psi_v'],lambda_u=lu,lambda_v=lv)
    result=second_variations(evaluate,psi,lam,s['u'],s['v'],37,s['preconditioner'],s['weights'],s['q'],first)
    proof=result['mixed_proof'];puv=result['psi_uv'];luv=result['lambda_uv']
    normalization=dot(psi,puv)+dot(first['psi_u'],first['psi_v'])
    if not normalization.enclosure().contains(0):raise ArithmeticError('normalization identity contradiction')
    rw=[arb(float(v)) for v in action.metric_data()[1]]
    payload=dict(algorithm='SHARED_ORIGINAL_DOMAIN_MIXED_EIGENLINE_V1',endpoint=19,
        radius_exact=s['radius_exact'],parameters=d.dimension,groups=d.groups,
        state_domain='x0+rL*dL*theta0+rT*D_T*thetaT; abs(theta0)<=1, norm2(thetaT)<=1',
        test_domain='independent u,v in the same full longitudinal/transverse product balls',
        auxiliary_domain='62 shared inherited eigenpair value-error coordinates; each reused everywhere',
        original_domain_unchanged=True,point_Hessian_recomputed=False,moving_value_recomputed=False,fifth_action_recomputed=False,
        inherited_first_eigenvector_solves_reused=True,missing_uniform_lambda_first_newly_enclosed=True,
        first_psi_u_models=[model(v) for v in first['psi_u']],first_lambda_u_model=model(lu),
        first_v_from_same_u_coefficients_by_exact_block_permutation=True,
        psi_uv_models=[model(v) for v in puv],lambda_uv_model=model(luv),
        psi_uv_raw_Euclidean_norm_upper=number(norm(puv)),
        psi_uv_physical_state_norm_upper=number(norm(puv,s['physical_weights'])),
        physical_state_norm_definition='norm2(W_state*(0_37,psi_uv))',
        psi_uv_rate_embedding_norm_upper=number(norm(puv,rw)),
        rate_embedding_norm_definition='norm2(W_reduced*psi_uv)',
        lambda_uv_absolute_upper=number(luv.support()),
        mixed_rhs_terms=[[model(v) for v in row] for row in result['mixed_rhs_terms']],
        mixed_rhs_term_order=['H_uv psi','H_u psi_v','H_v psi_u','lambda_u psi_v','lambda_v psi_u'],
        complete_mixed_rhs_models=[model(v) for v in result['complete_mixed_rhs_models']],
        normalization_border=model(result['normalization_border']),normalization_residual_model=model(normalization),
        normalization_residual_contains_zero=True,normalization_identity_enforced_by_bordered_system=True,
        bordered_predictor_preconditioned_residual_models=[model(v) for v in proof['preconditioned_residual_models']],
        weighted_residual_upper=number(proof['weighted_residual_upper']),
        weighted_correction_upper=number(proof['weighted_correction_upper']),reused_inverse_defect_upper=number(s['q']),
        same_shared_parameter_namespace=True,all_RHS_terms_combined_before_final_support=True,
        representation_limitation='First-order Taylor models keep common affine coefficients; bilinear and higher polynomial terms enter outward nonlinear tails. No signed bilinear polynomial certificate or sharpness claim is made.',
        source_SHA256=s['sources'],first_variation_import_receipt=s['import_receipt'],
        inherited_operand_receipt=s['inherited_operand_receipt'],new_contraction_receipts=evaluate.receipts,
        mixed_eigenline_enclosed=True,full_physical_remainder_enclosed=False,new_physical_budget_debit=False,
        Gate7_closed=False,kappa_L=None,kappa_T=None,FULL_BHSM_COMPLETE=False)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as f:f.write(encode(payload))
    print(json.dumps({k:payload[k] for k in ('psi_uv_raw_Euclidean_norm_upper','psi_uv_physical_state_norm_upper',
        'psi_uv_rate_embedding_norm_upper','lambda_uv_absolute_upper','weighted_correction_upper','mixed_eigenline_enclosed')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.work.resolve(),a.out.resolve())
