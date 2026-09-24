"""Complete endpoint-19 physical rate mixed jet, including the descriptor.

Consumes the new reproduced eigenline/response certificates. Cancels the
common border before normalization and reuses the frozen moving fifth leaf.
This endpoint field operator alone is not a full-history remainder or kappa.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,fmpq,ctx
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_mixed_eigenline_certificate as base
from bhsm.interface.shared_action_taylor import TaylorDomain,Taylor
from bhsm.interface.shared_complete_rate_jet import trilinear_jet,coupled_rate


class SymmetricEvaluator:
    """One action evaluation per unordered leg set and u/v-swap orbit."""
    def __init__(self,source,work):self.s=source;self.work=work;self.receipts=[]
    def __call__(self,legs):
        d=self.s['domain']
        legs=[[v if isinstance(v,Taylor) else d.affine(v) for v in leg] for leg in legs]
        if any(all(v.support().is_zero() for v in leg) for leg in legs):return d.affine(0)
        def canonical(items):
            paired=[(base.encode([base.model(v) for v in leg]),leg) for leg in items]
            paired.sort(key=lambda p:p[0]);return [p[1] for p in paired]
        plain=canonical(legs);flipped=canonical([[base.swap(v) for v in leg] for leg in legs])
        serialize=lambda ls:[[base.model(v) for v in leg] for leg in ls]
        plain_data,flip_data=serialize(plain),serialize(flipped)
        flip=base.encode(flip_data)<base.encode(plain_data)
        chosen,data=(flipped,flip_data) if flip else (plain,plain_data)
        key=base.digest(dict(legs=data,source_SHA256=self.s['sources']))
        path=self.work/f'{key}.json';completion=self.work/'completed'/f'{key}.json'
        if path.exists():
            record=json.loads(path.read_bytes())
            if record['key']!=key:raise ArithmeticError('cached action binding mismatch')
            if completion.exists() and json.loads(completion.read_bytes())['payload_SHA256']!=base.sha(path):
                raise ArithmeticError('completed action hash mismatch')
            value=base.unmodel(d,record['models'][0])
        else:
            print(json.dumps(dict(phase='NEW_DESCRIPTOR_JET_ACTION',order=len(legs),key=key)),flush=True)
            progress=lambda done,total:print(json.dumps(dict(phase='ACTION_QUADRATURE',key=key[:10],completed=done,total=total)),flush=True)
            value=base.contract(base.action,self.s['state'],chosen,progress)[0]
            record=dict(key=key,models=[base.model(value)])
            pending=path.with_suffix('.pending');pending.write_bytes(base.encode(record));os.replace(pending,path)
        completion.parent.mkdir(exist_ok=True)
        proof=dict(completed=True,key=key,payload_SHA256=base.sha(path),rows=1,parameters=d.dimension,
            groups=d.groups,radius_exact=self.s['radius_exact'],source_input_hashes=self.s['sources'],
            original_domain_unchanged=True,immutable_inputs_SHA256=base.sha(self.work/'immutable_inputs.json'))
        if not completion.exists():
            pending=completion.with_suffix('.pending');pending.write_bytes(base.encode(proof));os.replace(pending,completion)
        self.receipts.append(dict(key=key,SHA256=base.sha(path),u_v_permutation=flip,action_leg_symmetry_used=True))
        return base.swap(value) if flip else value


def run(evidence,work,out):
    ctx.prec=512;work.mkdir(parents=True,exist_ok=True)
    ep=ROOT/'artifacts/flagship_integration/gate7_mixed_eigenline_20260923'
    rp=ROOT/'artifacts/flagship_integration/gate7_mixed_response_20260923'
    eig=json.loads((ep/'certificate.json').read_bytes());response=json.loads((rp/'certificate.json').read_bytes())
    for p in (ep,rp):
        receipt=json.loads((p/'reproduction.json').read_bytes())
        if not receipt['byte_identical'] or receipt['first_SHA256']!=base.sha(p/'certificate.json'):
            raise ValueError('reproduced eigenline and response certificates required')
    s=base.operands(evidence,work);d=TaylorDomain(response['groups'],response['parameters'])
    s['domain']=d
    for key in ('state','u','v','moving'):s[key]=[base.unmodel(d,base.model(v)) for v in s[key]]
    load=lambda values:[base.unmodel(d,v) for v in values]
    pu=load(eig['first_psi_u_models']);qu=load(response['response_u_models'])
    psi=dict(value=s['moving'][:61],u=pu,v=[base.swap(v) for v in pu],uv=load(eig['psi_uv_models']))
    qr=dict(value=load(response['primal_response_models']),u=qu,v=[base.swap(v) for v in qu],uv=load(response['response_uv_models']))
    h={k:values[:61] for k,values in qr.items()};b={k:values[-1] for k,values in qr.items()}
    zero=d.affine(0)
    scalar=dict(value=base.unmodel(d,response['descriptor_model']),u=base.unmodel(d,response['descriptor_u_model']),uv=zero)
    scalar['v']=base.swap(scalar['u'])
    qw,rw,_,_=base.action.metric_data();qw=[arb(float(v)) for v in qw];rw=[arb(float(v)) for v in rw]
    weights_path=base.action.ENDPOINT.with_suffix('.npz')
    with np.load(weights_path,allow_pickle=False) as z:w=[arb(float(v)) for v in z['state_weights']]
    c=dict(value=[qw[i]*s['state'][37+i] for i in range(37)],
           u=[qw[i]*s['u'][37+i] for i in range(37)],v=[qw[i]*s['v'][37+i] for i in range(37)],uv=[zero]*37)
    p={k:[zero]*37+values for k,values in psi.items()}
    a={k:[zero]*37+[rw[i]*values[i]/w[37+i] for i in range(61)] for k,values in psi.items()}
    rawd={k:[c[k][i]/w[i] for i in range(37)]+[rw[i]*h[k][i]/w[37+i] for i in range(61)] for k in psi}
    valuepath=evidence/'artifacts/flagship_integration/.coupled_normalized_physical_value_work/endpoint_019'
    header=json.loads((valuepath/'record.json').read_bytes());vr=json.loads((valuepath/'reproduction.json').read_bytes())
    if not vr['byte_identical'] or not header['report']['validation_passed']:
        raise ValueError('frozen descriptor value certificate required')
    with np.load(valuepath/'value.npz',allow_pickle=False) as z:vals=base.read_array(z,'complete_descriptor_contractions')
    fifth_path=ROOT/'artifacts/flagship_integration/gate7_moving_response_20260923/action.json'
    fifth=json.loads(fifth_path.read_bytes())
    if fifth['radius_exact']!=s['radius_exact'] or not fifth['moving_eigenvector_values_enclosed']:
        raise ValueError('same original-domain moving fifth-action leaf required')
    old_eigen=[h for p,h in fifth['source_SHA256'].items() if p.replace('\\','/').endswith('/eigenpair_first.json')]
    eigen_path=ROOT/'artifacts/flagship_integration/gate7_moving_response_20260923/eigenpair.json'
    if old_eigen!=[base.sha(eigen_path)] or fifth['inherited_operand_receipt']!=s['inherited_operand_receipt']:
        raise ValueError('frozen fifth leaf uses different moving eigenpair or action operands')
    paths=[ep/'certificate.json',ep/'reproduction.json',rp/'certificate.json',rp/'reproduction.json',
        valuepath/'record.json',valuepath/'reproduction.json',valuepath/'value.npz',fifth_path,
        Path(__file__),ROOT/'src/bhsm/interface/shared_complete_rate_jet.py',ROOT/'src/bhsm/interface/shared_positive_norm_jet.py']
    s['sources'].update({str(p.resolve()):base.sha(p) for p in paths})
    if s['sources'][str((valuepath/'value.npz').resolve())]!=header['data_SHA256'] or s['sources'][str((valuepath/'record.json').resolve())]!=vr['record_SHA256']:
        raise ValueError('descriptor value input hashes do not reconcile')
    receipt=dict(source_input_hashes=s['sources'],inherited_operand_receipt=s['inherited_operand_receipt'],
        radius_exact=s['radius_exact'],parameters=d.dimension,groups=d.groups,original_domain_unchanged=True)
    receipt_path=work/'immutable_inputs.json';raw=base.encode(receipt)
    if receipt_path.exists():
        if receipt_path.read_bytes()!=raw:raise ValueError('full-rate input receipt changed')
    else:
        pending=receipt_path.with_suffix('.pending');pending.write_bytes(raw);os.replace(pending,receipt_path)
    evaluator=SymmetricEvaluator(s,work)
    leaf=d.affine(0,remainder=arb(fmpq(fifth['uniform_absolute_upper']['exact'])))
    print(json.dumps(dict(phase='COMPLETE_C_JET',frozen_fifth_action_reused=True)),flush=True)
    C=trilinear_jet(evaluator,[p,p,a],s['u'],s['v'],d.affine(vals[0]),leaf)
    print(json.dumps(dict(phase='COMPLETE_J_JET',C_uv_upper=base.number(C['uv'].support()))),flush=True)
    J=trilinear_jet(evaluator,[p,p,rawd],s['u'],s['v'],d.affine(vals[1]))
    # The b enclosure belongs to the same shared implicit solution. If this
    # model loses its sign, consume the already bound original response box.
    b_lower=b['value'].enclosure().lower()
    if not b_lower>0:raise ArithmeticError('positive shared response border enclosure unavailable')
    rate=coupled_rate(psi,h,b,scalar,c,rw,C,J,b_lower)
    if len(rate['mixed'])!=99:raise ArithmeticError('complete 99-component rate required')
    payload=dict(algorithm='SHARED_ORIGINAL_DOMAIN_COMPLETE_ENDPOINT_RATE_MIXED_V1',endpoint=19,
        radius_exact=s['radius_exact'],parameters=d.dimension,groups=d.groups,original_domain_unchanged=True,
        independent_coordinate_domain_substitution=False,common_shared_u_v_retained=True,
        moving_action_trilinear_C_jet={k:base.model(v) for k,v in C.items()},
        moving_action_trilinear_J_jet={k:base.model(v) for k,v in J.items()},
        complete_99_component_mixed_models=[base.model(v) for v in rate['mixed']],
        complete_weighted_physical_rate_mixed_norm_upper=base.number(base.norm(rate['mixed'])),
        state_98_mixed_norm_upper=base.number(base.norm(rate['mixed'][:98])),
        normalized_descriptor_mixed_absolute_upper=base.number(rate['mixed'][-1].support()),
        factored_descriptor_numerator_mixed=base.model(rate['descriptor_numerator_uv']),
        factored_norm_model=base.model(rate['norm']),factored_norm_uv_model=base.model(rate['norm_uv']),
        factored_norm_lower_exact='1',positive_border_lower=base.number(b_lower),
        coupled_orthogonality_and_normalization_reused=True,common_border_canceled_before_differentiation=True,
        all_16_moving_trilinear_mixed_assignments_included=True,frozen_fifth_action_recomputed=False,
        new_contraction_receipts=evaluator.receipts,source_SHA256=s['sources'],
        immutable_inputs_SHA256=base.sha(receipt_path),
        complete_endpoint_19_physical_field_Hessian_enclosed=True,full_history_midpoint_composition_enclosed=False,
        booked_quadratic_and_entry_mask_applied=False,new_physical_budget_debit=False,
        representation_limitation='Shared affine Taylor coefficients are retained; higher-degree u/v monomials and inherited coefficient uncertainty are enclosed by outward tails. This is a finite field bound, not a signed booked-history remainder.',
        Gate7_closed=False,kappa_L=None,kappa_T=None,FULL_BHSM_COMPLETE=False)
    pending=out.with_suffix('.pending');pending.write_bytes(base.encode(payload));os.replace(pending,out)
    print(json.dumps({k:payload[k] for k in ('complete_weighted_physical_rate_mixed_norm_upper','state_98_mixed_norm_upper',
        'normalized_descriptor_mixed_absolute_upper','complete_endpoint_19_physical_field_Hessian_enclosed')}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--evidence-root',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();run(a.evidence_root.resolve(),a.work.resolve(),a.out.resolve())
