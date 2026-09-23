"""Package only the new moving-eigenpair evidence and its exact repeats.

No numerical producer is invoked; inherited frozen evidence is consumed by
receipt. Output paths do not enter scientific certificate bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def sha(data):return hashlib.sha256(data).hexdigest().upper()
def encoded(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()


def package(work,out):
    records={};files={};receipts={}
    for name in ('eigenpair','action'):
        a,b=work/f'{name}_first.json',work/f'{name}_repeat.json'
        first,repeat=a.read_bytes(),b.read_bytes()
        if first!=repeat:raise ArithmeticError(f'{name} complete certificates differ')
        records[name]=json.loads(first)
        receipts[name]=dict(algorithm='EXACT_NEW_CERTIFICATE_REPRODUCTION_V1',
            first_path=str(a.resolve()),repeat_path=str(b.resolve()),
            first_SHA256=sha(first),repeat_SHA256=sha(repeat),byte_count=len(first),
            full_certificate_bytes_equal=True,rounded_decimal_comparison_used=False,
            inherited_frozen_numerical_calculations_rerun=False)
        files[f'{name}.json']=first
        files[f'{name}.reproduction.json']=encoded(receipts[name])
    eigen,action=records['eigenpair'],records['action']
    eigen_key=str((work/'eigenpair_first.json').resolve())
    if action['source_SHA256'][eigen_key]!=receipts['eigenpair']['first_SHA256']:
        raise ValueError('moving action must consume this exact eigenpair certificate')
    if action['radius_exact']!=eigen['radius_exact']:
        raise ValueError('original state domain must agree')
    sources=[Path(__file__),ROOT/'src/bhsm/interface/shared_implicit_response_jet.py',
             ROOT/'src/bhsm/interface/shared_eigenline_jet.py',
             ROOT/'tests/test_shared_implicit_response_jet.py']
    result=dict(algorithm='MOVING_RESPONSE_CHECKPOINT_V1',endpoint=19,stop_condition='B',
        moving_eigenpair_value_certificate_SHA256=receipts['eigenpair']['first_SHA256'],
        moving_fifth_action_certificate_SHA256=receipts['action']['first_SHA256'],
        maximum_eigenvector_affine_tail=eigen['maximum_eigenvector_remainder_upper'],
        eigenvalue_affine_tail=eigen['eigenvalue_remainder_upper'],
        moving_fifth_action_uniform_absolute_upper=action['uniform_absolute_upper'],
        first_missing_operator='E_uv(theta;u,v)=(D2 psi(x(theta))[D_r*u,D_r*v],D2 lambda(x(theta))[D_r*u,D_r*v])',
        missing_operator_equation='K*(psi_uv,-lambda_uv)=(-H_uv*psi-H_u*psi_v-H_v*psi_u+lambda_u*psi_v+lambda_v*psi_u,-psi_u^T*psi_v)',
        smallest_action_producer='bhsm.interface.shared_eigenline_jet.second_variations',
        action_derivative_orders_required=[2,3,4],
        missing_operator_BHSM_evaluation_completed=False,
        next_dependencies=['physical response mixed jet','positive shared normalization','actual midpoint/output/causal composition and booking mask'],
        stage_scope='New bound is one raw action leaf with moving eigenpair values, not the physical second derivative.',
        complete_physical_Hessian_enclosed=False,global_feasibility_established=False,
        kappa_L=None,kappa_T=None,
        kappa_targets={'L':'0.6542911248664067','T':'0.7452414479024602'},
        physical_inequalities={k:dict(certified_LHS=None,rigorous_margin=None,verdict='FAIL_TO_CERTIFY_UNKNOWN')
                              for k in ('longitudinal_self_map','transverse_self_map','contraction')},
        new_physical_ledger_debit=False,original_domain_shrunk=False,
        frozen_fixed_leg_recomputed=False,point_hessian_recomputed=False,
        new_numerical_certificates_independently_reproduced=True,
        focused_test_command='python -m pytest -q tests/test_shared_implicit_response_jet.py',
        source_SHA256={str(p.resolve()):sha(p.read_bytes()) for p in sources},
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    files['result.json']=encoded(result)
    out.mkdir(parents=True,exist_ok=False)
    for name,data in files.items():
        with (out/name).open('xb') as f:f.write(data)
    print(json.dumps(dict(certificates_equal=True,files={k:sha(v) for k,v in files.items()},
                         stop_condition='B',Gate7_closed=False)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();package(a.work.resolve(),a.out.resolve())
